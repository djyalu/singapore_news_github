# Singapore News Scraper Installation Guide

This guide provides step-by-step instructions for setting up the Singapore News Scraper system.

## Prerequisites

- GitHub account
- Vercel account (free tier is sufficient)
- Google account (for Gemini API)
- WhatsApp Business account (for Green API)
- Basic knowledge of Git and command line

## Quick Start (15 minutes)

### Step 1: Fork the Repository

1. Go to [https://github.com/djyalu/singapore_news_github](https://github.com/djyalu/singapore_news_github)
2. Click the "Fork" button in the top-right corner
3. Select your GitHub account as the destination

### Step 2: Enable GitHub Pages

1. Go to your forked repository
2. Navigate to Settings → Pages
3. Under "Source", select "Deploy from a branch"
4. Select "main" branch and "/ (root)" folder
5. Click "Save"
6. Your dashboard will be available at: `https://[your-username].github.io/singapore_news_github/`

### Step 3: Deploy to Vercel

1. Go to [https://vercel.com](https://vercel.com)
2. Sign in with your GitHub account
3. Click "New Project"
4. Import your forked repository
5. Configure environment variables:
   ```
   GITHUB_TOKEN=your_github_token
   GITHUB_OWNER=your_github_username
   GITHUB_REPO=singapore_news_github
   WHATSAPP_API_KEY=your_whatsapp_api_key
   ```
6. Click "Deploy"

### Step 4: Create GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings
2. Click "Personal access tokens" → "Tokens (classic)"
3. Click "Generate new token (classic)"
4. Set expiration (recommend: 90 days)
5. Select scopes:
   - ✅ repo (Full control of private repositories)
   - ✅ workflow (Update GitHub Action workflows)
6. Click "Generate token"
7. Copy the token (starts with `ghp_`)
8. Save it in Vercel environment variables as `GITHUB_TOKEN`

### Step 5: Set up Google Gemini API

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key
5. In your GitHub repository:
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `GOOGLE_GEMINI_API_KEY`
   - Value: [paste your API key]
   - Click "Add secret"

### Step 6: Configure WhatsApp (Green API)

1. Sign up at [Green API](https://green-api.com)
2. Get your Instance ID and API Token
3. Format your API key as: `{instanceId}:{apiToken}`
4. Add to Vercel environment variables as `WHATSAPP_API_KEY`

### Step 7: Enable GitHub Actions

1. Go to your repository → Actions tab
2. If you see "Workflows aren't being run", click "I understand my workflows, go ahead and enable them"
3. Enable all workflows:
   - Singapore News Scraper
   - Scrape News Only
   - Send to WhatsApp
   - Keep Alive Workflow

### Step 8: Initial Configuration

1. Visit your dashboard: `https://[your-username].github.io/singapore_news_github/`
2. Login with default credentials:
   - Username: `admin`
   - Password: `Admin@123`
3. **Important**: Change the password immediately in Settings

## Detailed Setup Instructions

### Environment Variables Reference

#### Vercel Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | `ghp_xxxxxxxxxxxxxxxxxxxx` |
| `GITHUB_OWNER` | Your GitHub username | `johndoe` |
| `GITHUB_REPO` | Repository name | `singapore_news_github` |
| `WHATSAPP_API_KEY` | Green API credentials | `instanceId:apiToken` |

#### GitHub Secrets

| Secret | Description | Required |
|--------|-------------|----------|
| `GOOGLE_GEMINI_API_KEY` | Google Gemini API key | Yes |

### WhatsApp Channel Setup

1. Create WhatsApp groups for news distribution
2. Add the Green API bot to your groups
3. Get group IDs:
   - Send any message to the group
   - Check Green API dashboard for group ID
   - Format: `120363xxxxxxxxxxxxx@g.us`
4. Update channel IDs in Settings

### Customizing News Sources

Edit `data/sites.json` to add/remove news sources:

```json
{
  "sites": [
    {
      "name": "The Straits Times",
      "url": "https://www.straitstimes.com",
      "group": "News",
      "enabled": true
    }
  ]
}
```

### Scheduling Configuration

Default schedule (in `.github/workflows/scraper.yml`):
```yaml
schedule:
  - cron: '55 22 * * *'  # 07:55 KST daily
```

To change the schedule:
1. Edit the cron expression
2. Commit and push changes
3. GitHub Actions will use the new schedule

Cron expression examples:
- `0 0 * * *` - Midnight UTC daily
- `0 */6 * * *` - Every 6 hours
- `0 9,13,18 * * *` - 9am, 1pm, 6pm UTC

### Scraping Methods

Configure in Settings → Scraping Method:

1. **Traditional**: HTML parsing with BeautifulSoup
   - Fast and reliable
   - May miss some dynamic content
   
2. **AI**: Google Gemini powered extraction
   - Better content understanding
   - Handles dynamic sites better
   - Uses API quota

3. **RSS**: RSS feed parsing
   - Most reliable
   - Limited to sites with RSS

4. **Hybrid** (Recommended): RSS + Traditional fallback
   - Best coverage
   - Optimal reliability

## Troubleshooting

### Common Issues

#### 1. "GitHub Token Expired"
- Generate a new token following Step 4
- Update in Vercel environment variables
- Redeploy Vercel project

#### 2. "WhatsApp Send Failed"
- Verify Green API credentials
- Check if bot is in the WhatsApp group
- Ensure group ID is correct

#### 3. "Scraping Returns 0 Articles"
- Check if news sites are accessible
- Try different scraping method
- Verify site selectors in `scraper.py`

#### 4. "GitHub Actions Not Running"
- Ensure workflows are enabled
- Check if repository has been inactive for 60+ days
- Push a commit to reactivate

#### 5. "API Endpoint Error"
- Check Vercel deployment logs
- Verify all environment variables
- Ensure Vercel project is active

### Verification Steps

1. **Test Environment Variables**:
   - Visit: `https://your-vercel-app.vercel.app/api/test-env`
   - Should show all variables as "configured"

2. **Test WhatsApp**:
   - Use dashboard "Test WhatsApp" button
   - Should receive test message

3. **Test Scraping**:
   - Click "지금 스크랩하기" (Scrape Now)
   - Monitor progress in status section

## Security Best Practices

1. **Change Default Password**: First login action
2. **Rotate Tokens**: Every 90 days
3. **Limit Repository Access**: Private repository recommended
4. **Monitor Usage**: Check GitHub Actions minutes
5. **API Keys**: Never commit to repository

## Maintenance

### Daily Tasks
- Monitor scraping success via dashboard
- Check WhatsApp delivery

### Weekly Tasks
- Review scraped article quality
- Clean up old data (automatic after 30 days)
- Check API usage limits

### Monthly Tasks
- Update news site selectors if needed
- Review and rotate API tokens
- Check for repository updates

## Support

For issues or questions:
1. Check [Troubleshooting Guide](./TROUBLESHOOTING_GUIDE.md)
2. Review [API Documentation](./API_DOCUMENTATION.md)
3. Create issue on GitHub repository

## Next Steps

1. Customize news sources for your needs
2. Set up monitoring alerts
3. Configure backup WhatsApp channels
4. Adjust scraping schedule
5. Invite team members (create accounts in Settings)