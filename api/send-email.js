const nodemailer = require('nodemailer');

module.exports = async (req, res) => {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { recipients, subject, body, isTest = false } = req.body;

        if (!recipients || !recipients.length) {
            return res.status(400).json({
                success: false,
                error: '수신자 이메일이 필요합니다.'
            });
        }

        // SMTP 설정 (환경 변수에서 가져오기)
        const smtpUser = process.env.SMTP_USER;
        const smtpPassword = process.env.SMTP_PASSWORD;
        const smtpHost = process.env.SMTP_HOST || 'smtp.gmail.com';
        const smtpPort = process.env.SMTP_PORT || 587;

        if (!smtpUser || !smtpPassword) {
            return res.status(500).json({
                success: false,
                error: 'SMTP 설정이 완료되지 않았습니다.'
            });
        }

        // Nodemailer 트랜스포터 생성
        const transporter = nodemailer.createTransport({
            host: smtpHost,
            port: smtpPort,
            secure: false, // true for 465, false for other ports
            auth: {
                user: smtpUser,
                pass: smtpPassword
            }
        });

        // 이메일 내용 생성
        const htmlBody = `
        <html>
          <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #333;">🔔 Singapore News Scraper ${isTest ? '테스트' : '알림'}</h2>
              <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                ${body}
              </div>
              <hr style="margin: 20px 0;">
              <p style="color: #666; font-size: 12px;">
                이 메일은 Singapore News Scraper 시스템에서 자동 발송되었습니다.<br>
                설정 변경은 <a href="https://djyalu.github.io/singapore_news_github/">대시보드</a>에서 가능합니다.
              </p>
            </div>
          </body>
        </html>
        `;

        // 이메일 옵션
        const mailOptions = {
            from: `Singapore News Scraper <${smtpUser}>`,
            to: recipients.join(', '),
            subject: subject || '🔔 Singapore News Scraper 알림',
            html: htmlBody,
            text: body.replace(/<[^>]*>/g, '') // HTML 태그 제거
        };

        // 이메일 전송
        const info = await transporter.sendMail(mailOptions);

        console.log('Email sent:', info.messageId);

        return res.status(200).json({
            success: true,
            messageId: info.messageId,
            recipients: recipients
        });

    } catch (error) {
        console.error('Email sending error:', error);
        return res.status(500).json({
            success: false,
            error: error.message || '이메일 전송 중 오류가 발생했습니다.'
        });
    }
};