#!/usr/bin/env python3
"""
Quick SMTP test - checks if Gmail SMTP is accessible
"""

import smtplib
import socket

def test_smtp_connection():
    print("🔌 Testing SMTP connection to Gmail...")
    
    try:
        # Test basic connectivity
        print("1. Testing network connectivity...")
        socket.create_connection(("smtp.gmail.com", 587), timeout=10)
        print("✅ Network connection to smtp.gmail.com:587 successful")
        
        # Test SMTP server response
        print("2. Testing SMTP server response...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("✅ SMTP server response and TLS connection successful")
        server.quit()
        
        print("\n🎉 SMTP configuration is working!")
        print("📝 Next steps:")
        print("1. Use your Gmail address and app password")
        print("2. Test from the dashboard or with actual credentials")
        
    except socket.timeout:
        print("❌ Network timeout - check internet connection")
    except socket.gaierror:
        print("❌ DNS resolution failed for smtp.gmail.com")
    except Exception as e:
        print(f"❌ SMTP test failed: {e}")
        print("\n🔍 Common issues:")
        print("- Firewall blocking port 587")
        print("- Gmail SMTP server temporarily unavailable")
        print("- Network connectivity issues")

if __name__ == "__main__":
    test_smtp_connection()