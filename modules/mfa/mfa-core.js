/**
 * MFA Core Module
 * 핵심 MFA 기능 (TOTP 생성, 검증, Base32 인코딩/디코딩)
 */

export const MFACore = {
    /**
     * Base32 문자열을 hex로 디코딩
     */
    base32Decode(secret) {
        const base32Chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
        let bits = '';
        let hex = '';
        
        // Remove spaces and convert to uppercase
        secret = secret.replace(/\s/g, '').toUpperCase();
        
        for (let i = 0; i < secret.length; i++) {
            const val = base32Chars.indexOf(secret.charAt(i));
            if (val === -1) throw new Error('Invalid base32 character');
            bits += val.toString(2).padStart(5, '0');
        }
        
        for (let i = 0; i + 8 <= bits.length; i += 8) {
            hex += parseInt(bits.substr(i, 8), 2).toString(16).padStart(2, '0');
        }
        
        return hex;
    },

    /**
     * Hex 문자열을 바이트 배열로 변환
     */
    hexToBytes(hex) {
        const bytes = [];
        for (let i = 0; i < hex.length; i += 2) {
            bytes.push(parseInt(hex.substr(i, 2), 16));
        }
        return new Uint8Array(bytes);
    },

    /**
     * HOTP (HMAC-based One-Time Password) 생성
     */
    async generateHOTP(secret, counter) {
        const key = this.hexToBytes(this.base32Decode(secret));
        const counterBytes = new Uint8Array(8);
        
        // Convert counter to 8-byte array (big-endian)
        for (let i = 7; i >= 0; i--) {
            counterBytes[i] = counter & 0xff;
            counter = Math.floor(counter / 256);
        }
        
        // Import the key
        const cryptoKey = await crypto.subtle.importKey(
            'raw',
            key,
            { name: 'HMAC', hash: 'SHA-1' },
            false,
            ['sign']
        );
        
        // Generate HMAC
        const signature = await crypto.subtle.sign('HMAC', cryptoKey, counterBytes);
        const signatureArray = new Uint8Array(signature);
        
        // Dynamic truncation
        const offset = signatureArray[signatureArray.length - 1] & 0x0f;
        const code = (
            ((signatureArray[offset] & 0x7f) << 24) |
            ((signatureArray[offset + 1] & 0xff) << 16) |
            ((signatureArray[offset + 2] & 0xff) << 8) |
            (signatureArray[offset + 3] & 0xff)
        ) % 1000000;
        
        return code.toString().padStart(6, '0');
    },

    /**
     * TOTP (Time-based One-Time Password) 검증
     */
    async verifyTOTP(secret, token, windowSize = 2) {
        try {
            const timeStep = 30; // 30 seconds
            const currentTime = Math.floor(Date.now() / 1000);
            const currentCounter = Math.floor(currentTime / timeStep);
            
            // Check current window and adjacent windows (for time sync issues)
            for (let i = -windowSize; i <= windowSize; i++) {
                const counter = currentCounter + i;
                const expectedToken = await this.generateHOTP(secret, counter);
                
                if (expectedToken === token.toString().padStart(6, '0')) {
                    return true;
                }
            }
            
            return false;
        } catch (error) {
            console.error('TOTP verification error:', error);
            return false;
        }
    },

    /**
     * Secret 키 생성
     */
    generateSecret(length = 16) {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
        let secret = '';
        for (let i = 0; i < length; i++) {
            secret += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return secret;
    },

    /**
     * OTP Auth URL 생성 (QR 코드용)
     */
    generateOTPAuthURL(secret, username, issuer = 'Singapore News Scraper') {
        return `otpauth://totp/${issuer}:${username}?secret=${secret}&issuer=${issuer}`;
    }
};