# Singapore News Scraper Documentation

Welcome to the comprehensive documentation for the Singapore News Scraper project. This documentation covers everything from installation to advanced troubleshooting.

## 📚 Documentation Overview

### Getting Started
- **[Installation Guide](./INSTALLATION_GUIDE.md)** - Step-by-step setup instructions
- **[Quick Start](../README.md)** - Basic overview and quick setup

### User Documentation
- **[User Guide](./USER_GUIDE.md)** - Comprehensive guide for end users
- **[사용자 매뉴얼 (Korean)](../USER_MANUAL.md)** - Korean user manual
- **[상세 사용자 매뉴얼 v1.1.0](./USER_MANUAL_DETAILED.md)** - Detailed user manual with v1.1.0 features

### Developer Documentation
- **[Developer Guide](./DEVELOPER_GUIDE.md)** - Technical guide for developers
- **[API Documentation](./API_DOCUMENTATION.md)** - Complete API reference
- **[Architecture Overview](./DEPLOYMENT_STRUCTURE.md)** - System architecture details

### Configuration & Setup
- **[Vercel Setup](./VERCEL_SETUP.md)** - Vercel deployment guide
- **[GitHub Pages Setup](../GITHUB_PAGES_SETUP.md)** - Frontend deployment
- **[Green API Setup](../GREEN_API_SETUP.md)** - WhatsApp integration setup

### Troubleshooting & Support
- **[Troubleshooting Guide](./TROUBLESHOOTING_GUIDE.md)** - Common issues and solutions
- **[Monitoring Guide](../MONITORING_GUIDE.md)** - System monitoring setup

### Advanced Topics
- **[AI Optimization Guide](../AI_OPTIMIZATION_GUIDE.md)** - AI scraping optimization
- **[Security Update](../SECURITY_UPDATE.md)** - Security best practices
- **[Content Duplication Fix](../CONTENT_DUPLICATION_FIX.md)** - Deduplication system

## 🗂️ Documentation Structure

```
docs/
├── README.md                    # This file - Documentation index
├── API_DOCUMENTATION.md         # Complete API reference
├── DEVELOPER_GUIDE.md          # Developer documentation
├── INSTALLATION_GUIDE.md       # Installation instructions
├── TROUBLESHOOTING_GUIDE.md    # Troubleshooting guide
├── USER_GUIDE.md              # User documentation
├── DEPLOYMENT_STRUCTURE.md     # Architecture details
└── VERCEL_SETUP.md            # Vercel configuration

Related documentation in root:
├── README.md                   # Project overview
├── CLAUDE.md                  # AI assistant reference
├── USER_MANUAL.md             # Korean user manual
├── MONITORING_GUIDE.md        # Monitoring setup
├── GREEN_API_SETUP.md         # WhatsApp setup
├── AI_OPTIMIZATION_GUIDE.md   # AI optimization
└── Various setup guides...
```

## 🚀 Quick Links

### For Users
1. [How to login](./USER_GUIDE.md#로그인)
2. [How to scrape news](./USER_GUIDE.md#뉴스-스크래핑)
3. [How to send WhatsApp messages](./USER_GUIDE.md#whatsapp-전송)
4. [Managing settings](./USER_GUIDE.md#설정-관리)

### For Developers
1. [Local development setup](./DEVELOPER_GUIDE.md#development-setup)
2. [Adding new features](./DEVELOPER_GUIDE.md#adding-new-features)
3. [API endpoint reference](./API_DOCUMENTATION.md#api-endpoints-overview)
4. [Deployment process](./DEVELOPER_GUIDE.md#deployment)

### For Administrators
1. [Initial setup](./INSTALLATION_GUIDE.md#quick-start-15-minutes)
2. [User management](./USER_GUIDE.md#사용자-관리)
3. [System monitoring](../MONITORING_GUIDE.md)
4. [Troubleshooting](./TROUBLESHOOTING_GUIDE.md#quick-diagnostics)

## 📊 System Overview

The Singapore News Scraper is an automated system that:
- 🌏 Scrapes news from 16+ Singapore news websites
- 🤖 Generates Korean summaries using Google Gemini AI
- 📱 Sends daily digests via WhatsApp
- ⏰ Runs automatically on schedule
- 🔧 Provides web dashboard for management

### Key Components
1. **Frontend**: GitHub Pages hosted dashboard
2. **API**: Vercel serverless functions
3. **Automation**: GitHub Actions workflows
4. **Storage**: GitHub repository (JSON files)
5. **AI**: Google Gemini API
6. **Messaging**: WhatsApp Green API

## 🛠️ Technology Stack

- **Frontend**: HTML, JavaScript, Tailwind CSS
- **Backend**: Node.js (Vercel Functions)
- **Automation**: Python 3.x, GitHub Actions
- **APIs**: Google Gemini, WhatsApp Green API
- **Deployment**: GitHub Pages, Vercel

## 📝 Documentation Standards

All documentation follows these standards:
- Clear, concise language
- Step-by-step instructions with examples
- Screenshots and diagrams where helpful
- Regular updates with version changes
- Both English and Korean where appropriate

## 🤝 Contributing to Documentation

To improve documentation:
1. Fork the repository
2. Make your changes
3. Submit a pull request
4. Include:
   - What you changed
   - Why it was needed
   - Any new sections added

## 📞 Getting Help

If you need help:
1. Check the [Troubleshooting Guide](./TROUBLESHOOTING_GUIDE.md)
2. Review relevant documentation section
3. Search existing GitHub Issues
4. Create a new issue with:
   - Clear problem description
   - Steps to reproduce
   - Error messages
   - System configuration

## 🔄 Documentation Updates

Last updated: July 25, 2025

Recent changes:
- Added comprehensive API documentation
- Expanded troubleshooting guide
- Created developer guide
- Improved installation instructions
- Added user guide in Korean
- Created detailed user manual v1.1.0 with Cohere AI features

---

*This documentation is part of the Singapore News Scraper project. For the latest updates, visit the [GitHub repository](https://github.com/djyalu/singapore_news_github).*