"""
Test fixtures and sample data for Singapore News Scraper tests
"""
import json
from datetime import datetime, timedelta
import pytz

# Timezone
KST = pytz.timezone('Asia/Seoul')

def get_sample_article(
    title="Sample Article Title",
    url="https://example.com/article/123",
    site="The Straits Times",
    group="News",
    days_old=0
):
    """Generate a sample article with customizable fields"""
    now = datetime.now(KST)
    publish_date = now - timedelta(days=days_old)
    
    return {
        "title": title,
        "url": url,
        "summary": f"This is a summary of {title}. It contains important information about recent events in Singapore.",
        "content": f"Full content of {title}. " * 20,  # Longer content
        "site": site,
        "group": group,
        "publish_date": publish_date.isoformat(),
        "scraped_at": now.isoformat(),
        "author": "Test Author",
        "tags": ["Singapore", group.lower()],
        "extracted_by": "traditional",
        "language": "en",
        "word_count": 200
    }

def get_sample_scraped_data(num_articles=5, num_groups=3):
    """Generate sample scraped data file structure"""
    groups = ["News", "Economy", "Politics", "Technology", "Society", "Sports"][:num_groups]
    sites = ["The Straits Times", "Channel NewsAsia", "Business Times", "TODAY", "Mothership"]
    
    articles_by_group = {}
    total_count = 0
    
    for i, group in enumerate(groups):
        group_articles = []
        articles_in_group = min(num_articles // num_groups + (1 if i < num_articles % num_groups else 0), num_articles)
        
        for j in range(articles_in_group):
            article = get_sample_article(
                title=f"{group} Article {j+1}",
                url=f"https://example.com/{group.lower()}/{j+1}",
                site=sites[j % len(sites)],
                group=group,
                days_old=j
            )
            group_articles.append(article)
            total_count += 1
        
        if group_articles:
            articles_by_group[group] = {
                "group": group,
                "articles": group_articles,
                "article_count": len(group_articles),
                "sites": list(set(a["site"] for a in group_articles)),
                "timestamp": datetime.now(KST).isoformat()
            }
    
    return {
        "timestamp": datetime.now(KST).isoformat(),
        "articles": list(articles_by_group.values()),
        "stats": {
            "total": total_count,
            "byGroup": {g: len(articles_by_group.get(g, {}).get("articles", [])) for g in groups},
            "bySite": {},
            "scrapingMethod": "traditional",
            "duration": 45.2,
            "errors": 0
        },
        "metadata": {
            "version": "2.0",
            "scraper_version": "1.0.0",
            "settings": {
                "maxArticlesPerSite": 3,
                "scrapingMethod": "traditional"
            }
        }
    }

def get_sample_sites_config():
    """Get sample sites configuration"""
    return [
        {
            "name": "The Straits Times",
            "url": "https://www.straitstimes.com/singapore",
            "group": "News",
            "enabled": True,
            "selectors": {
                "article": "article.card",
                "title": "h3.card-title",
                "link": "a.card-link"
            }
        },
        {
            "name": "Channel NewsAsia",
            "url": "https://www.channelnewsasia.com/singapore",
            "group": "News",
            "enabled": True,
            "rss": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml"
        },
        {
            "name": "Business Times",
            "url": "https://www.businesstimes.com.sg",
            "group": "Economy",
            "enabled": True
        },
        {
            "name": "Mothership",
            "url": "https://mothership.sg",
            "group": "Society",
            "enabled": True,
            "rss": "https://mothership.sg/feed/"
        },
        {
            "name": "The Independent Singapore",
            "url": "https://theindependent.sg",
            "group": "Politics",
            "enabled": False
        }
    ]

def get_sample_settings():
    """Get sample settings configuration"""
    return {
        "scrapTarget": "recent",
        "importantKeywords": "economy,covid,election,hdb,transport",
        "blockedKeywords": "advertisement,sponsored,promotion",
        "summaryOptions": {
            "headline": True,
            "keywords": True,
            "content": True,
            "maxLength": 500
        },
        "sendChannel": "whatsapp",
        "whatsappChannel": "120363419092108413@g.us",
        "whatsappApiUrl": "https://api.green-api.com",
        "sendSchedule": {
            "period": "daily",
            "time": "08:00",
            "weekdays": [],
            "timezone": "Asia/Seoul"
        },
        "scrapingMethod": "traditional",
        "scrapingMethodOptions": {
            "traditional": {
                "useEnhancedFiltering": True,
                "timeout": 30
            },
            "ai": {
                "provider": "gemini",
                "model": "gemini-1.5-flash",
                "maxTokens": 1000,
                "temperature": 0.7,
                "fallbackToTraditional": True
            },
            "rss": {
                "maxArticlesPerFeed": 5,
                "includeFullContent": False
            },
            "hybrid_ai": {
                "useAIForSummary": True,
                "priorityBoost": 1.5
            }
        },
        "dataRetention": {
            "days": 30,
            "maxSizeMB": 100
        },
        "monitoring": {
            "enabled": True,
            "alertEmail": "admin@example.com"
        },
        "maxArticlesPerSite": 3,
        "maxArticlesPerGroup": 10,
        "totalArticleLimit": 50
    }

def get_sample_html_content(num_articles=10):
    """Generate sample HTML content for testing parsers"""
    articles_html = []
    
    for i in range(num_articles):
        articles_html.append(f"""
        <article class="card" data-article-id="{i}">
            <div class="card-body">
                <h3 class="card-title">
                    <a href="/singapore/article-{i}" class="card-link">
                        Breaking: Important News Story {i}
                    </a>
                </h3>
                <p class="card-summary">
                    This is a summary of article {i}. It contains important information
                    about recent developments in Singapore that citizens should know about.
                </p>
                <div class="card-meta">
                    <time datetime="2025-07-24T{10+i}:00:00+08:00" class="publish-time">
                        July 24, 2025, {10+i}:00 AM
                    </time>
                    <span class="author">By John Doe</span>
                    <span class="category">Singapore</span>
                </div>
            </div>
        </article>
        """)
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Singapore News - Test Page</title>
        <meta property="og:site_name" content="Test News Site">
        <meta property="article:section" content="Singapore">
    </head>
    <body>
        <header>
            <h1>Singapore News</h1>
            <nav>
                <a href="/singapore">Singapore</a>
                <a href="/asia">Asia</a>
                <a href="/world">World</a>
            </nav>
        </header>
        <main>
            <section class="latest-news">
                <h2>Latest Singapore News</h2>
                <div class="articles-container">
                    {''.join(articles_html)}
                </div>
            </section>
        </main>
        <footer>
            <p>&copy; 2025 Test News Site</p>
        </footer>
    </body>
    </html>
    """

def get_sample_rss_feed(num_entries=5):
    """Generate sample RSS feed content"""
    entries = []
    now = datetime.now(KST)
    
    for i in range(num_entries):
        pub_date = (now - timedelta(hours=i)).strftime('%a, %d %b %Y %H:%M:%S %z')
        entries.append(f"""
        <item>
            <title>RSS News Item {i+1}: Important Singapore Update</title>
            <link>https://example.com/rss/article-{i+1}</link>
            <description>This is the description for RSS item {i+1}. It contains a summary of the news story about Singapore.</description>
            <pubDate>{pub_date}</pubDate>
            <guid isPermaLink="true">https://example.com/rss/article-{i+1}</guid>
            <category>Singapore</category>
            <category>News</category>
            <author>editor@example.com (Editor Name)</author>
        </item>
        """)
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
        <channel>
            <title>Test News Site - Singapore Feed</title>
            <link>https://example.com</link>
            <description>Latest Singapore news and updates</description>
            <language>en-sg</language>
            <lastBuildDate>{now.strftime('%a, %d %b %Y %H:%M:%S %z')}</lastBuildDate>
            <atom:link href="https://example.com/feed" rel="self" type="application/rss+xml"/>
            {''.join(entries)}
        </channel>
    </rss>
    """

def get_sample_api_response(success=True, data_type="settings"):
    """Generate sample API response"""
    if not success:
        return {
            "success": False,
            "error": "Test error message",
            "code": "TEST_ERROR"
        }
    
    if data_type == "settings":
        return {
            "success": True,
            "data": get_sample_settings()
        }
    elif data_type == "sites":
        return {
            "success": True,
            "data": get_sample_sites_config()
        }
    elif data_type == "latest":
        return {
            "success": True,
            "data": get_sample_scraped_data(num_articles=3)
        }
    elif data_type == "status":
        return {
            "success": True,
            "data": {
                "status": "idle",
                "lastRun": datetime.now(KST).isoformat(),
                "nextRun": (datetime.now(KST) + timedelta(hours=1)).isoformat(),
                "stats": {
                    "totalRuns": 42,
                    "successfulRuns": 40,
                    "failedRuns": 2,
                    "averageDuration": 45.6
                }
            }
        }
    
    return {"success": True, "data": {}}