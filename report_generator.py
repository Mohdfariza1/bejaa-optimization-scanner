#!/usr/bin/env python3
"""
Bejaa Digital Website Optimization Scanner - Report Generator
Generates comprehensive HTML reports from scan results
"""

import json
import os
import re
from datetime import datetime
from urllib.parse import urlparse
import html

class ReportGenerator:
    """Generate comprehensive HTML reports from scan results"""
    
    def __init__(self, scan_results):
        self.results = scan_results
        self.url = scan_results.get('url', 'Unknown URL')
        self.scan_date = scan_results.get('scan_date', datetime.now().isoformat())
        self.overall_score = scan_results.get('overall_score', 0)
        self.grade = scan_results.get('grade', 'F')
        
    def generate_html_report(self):
        """Generate a comprehensive HTML report"""
        
        # Get category data
        categories = self.results.get('categories', {})
        recommendations = self.results.get('recommendations', [])
        connectivity = self.results.get('connectivity', {})
        
        # Calculate color based on score
        score_color = self._get_score_color(self.overall_score)
        grade_color = self._get_grade_color(self.grade)
        
        # Format date
        try:
            scan_date_obj = datetime.fromisoformat(self.scan_date.replace('Z', '+00:00'))
            formatted_date = scan_date_obj.strftime("%B %d, %Y at %I:%M %p")
        except:
            formatted_date = self.scan_date
        
        # Generate HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Optimization Report - {html.escape(self.url)}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .report-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .report-header {{
            background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .report-header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .report-header .url {{
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 30px;
            word-break: break-all;
        }}
        
        .score-display {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 40px;
            margin-top: 30px;
            flex-wrap: wrap;
        }}
        
        .overall-score {{
            text-align: center;
        }}
        
        .score-circle {{
            width: 180px;
            height: 180px;
            border-radius: 50%;
            background: conic-gradient({score_color} 0% {self.overall_score}%, #e0e0e0 {self.overall_score}% 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            margin: 0 auto 20px;
        }}
        
        .score-circle::before {{
            content: '';
            position: absolute;
            width: 160px;
            height: 160px;
            background: white;
            border-radius: 50%;
        }}
        
        .score-value {{
            position: relative;
            z-index: 1;
            font-size: 3.5rem;
            font-weight: 800;
            color: {score_color};
        }}
        
        .score-label {{
            font-size: 1.2rem;
            color: #666;
            margin-top: 5px;
        }}
        
        .grade-display {{
            text-align: center;
        }}
        
        .grade-circle {{
            width: 180px;
            height: 180px;
            border-radius: 50%;
            background: {grade_color};
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            color: white;
            font-size: 5rem;
            font-weight: 800;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .report-content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section-title {{
            font-size: 1.8rem;
            color: #1a237e;
            margin-bottom: 25px;
            padding-bottom: 10px;
            border-bottom: 3px solid #e0e0e0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-title i {{
            font-size: 1.5rem;
        }}
        
        .category-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        
        .category-card {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            border: 2px solid #e0e0e0;
            transition: all 0.3s ease;
        }}
        
        .category-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            border-color: #667eea;
        }}
        
        .category-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .category-title {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.3rem;
            font-weight: 600;
            color: #333;
        }}
        
        .category-score {{
            font-size: 1.8rem;
            font-weight: 700;
            padding: 8px 16px;
            border-radius: 50px;
            background: #e0e0e0;
        }}
        
        .score-excellent {{ background: #d4edda; color: #155724; }}
        .score-good {{ background: #d1ecf1; color: #0c5460; }}
        .score-fair {{ background: #fff3cd; color: #856404; }}
        .score-poor {{ background: #f8d7da; color: #721c24; }}
        
        .category-details {{
            margin-bottom: 20px;
        }}
        
        .detail-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .detail-label {{
            color: #666;
        }}
        
        .detail-value {{
            font-weight: 500;
            color: #333;
        }}
        
        .issues-list {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 0 8px 8px 0;
            margin-top: 15px;
        }}
        
        .issues-list h4 {{
            color: #856404;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .issues-list ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .issues-list li {{
            padding: 5px 0;
            color: #856404;
            display: flex;
            align-items: flex-start;
            gap: 8px;
        }}
        
        .issues-list li::before {{
            content: '⚠️';
            font-size: 0.9rem;
        }}
        
        .recommendations-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .recommendation-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            display: flex;
            align-items: flex-start;
            gap: 15px;
            transition: all 0.3s ease;
        }}
        
        .recommendation-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(102, 126, 234, 0.3);
        }}
        
        .recommendation-icon {{
            font-size: 1.5rem;
            margin-top: 2px;
        }}
        
        .recommendation-text {{
            flex: 1;
        }}
        
        .recommendation-text h4 {{
            margin-bottom: 10px;
            font-size: 1.1rem;
        }}
        
        .connectivity-info {{
            background: #e3f2fd;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        
        .info-item {{
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}
        
        .info-label {{
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .info-value {{
            font-size: 1.3rem;
            font-weight: 600;
            color: #333;
        }}
        
        .info-value.status-200 {{ color: #28a745; }}
        .info-value.status-error {{ color: #dc3545; }}
        
        .report-footer {{
            background: #f8f9fa;
            padding: 30px 40px;
            text-align: center;
            border-top: 1px solid #e0e0e0;
            color: #666;
        }}
        
        .footer-logo {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #1a237e;
            margin-bottom: 10px;
        }}
        
        .footer-info {{
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .report-header {{
                padding: 25px;
            }}
            
            .report-header h1 {{
                font-size: 1.8rem;
            }}
            
            .score-display {{
                flex-direction: column;
                gap: 20px;
            }}
            
            .report-content {{
                padding: 25px;
            }}
            
            .category-grid {{
                grid-template-columns: 1fr;
            }}
            
            .recommendations-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .print-button {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #1a237e;
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            z-index: 1000;
            transition: all 0.3s ease;
        }}
        
        .print-button:hover {{
            background: #283593;
            transform: translateY(-3px);
        }}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="report-container">
        <div class="report-header">
            <h1>Website Optimization Report</h1>
            <div class="url">{html.escape(self.url)}</div>
            <div class="scan-date">Scanned on {formatted_date}</div>
            
            <div class="score-display">
                <div class="overall-score">
                    <div class="score-circle">
                        <div class="score-value">{self.overall_score}</div>
                    </div>
                    <div class="score-label">Overall Score /100</div>
                </div>
                
                <div class="grade-display">
                    <div class="grade-circle">{self.grade}</div>
                    <div class="score-label">Overall Grade</div>
                </div>
            </div>
        </div>
        
        <div class="report-content">
            <!-- Connectivity Information -->
            <div class="section">
                <h2 class="section-title"><i class="fas fa-network-wired"></i> Connectivity Information</h2>
                <div class="connectivity-info">
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Status Code</div>
                            <div class="info-value status-{connectivity.get('status_code', 'N/A')}">{connectivity.get('status_code', 'N/A')}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Response Time</div>
                            <div class="info-value">{connectivity.get('response_time', 0):.3f}s</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Final URL</div>
                            <div class="info-value" style="word-break: break-all; font-size: 0.9rem;">{html.escape(connectivity.get('final_url', 'N/A'))}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Content Size</div>
                            <div class="info-value">{connectivity.get('content_length', 0):,} bytes</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Category Analysis -->
            <div class="section">
                <h2 class="section-title"><i class="fas fa-chart-bar"></i> Detailed Analysis</h2>
                <div class="category-grid">
                    {self._generate_category_cards(categories)}
                </div>
            </div>
            
            <!-- Recommendations -->
            <div class="section">
                <h2 class="section-title"><i class="fas fa-lightbulb"></i> Optimization Recommendations</h2>
                <div class="recommendations-grid">
                    {self._generate_recommendations(recommendations)}
                </div>
            </div>
            
            <!-- Missing Security Headers -->
            {self._generate_security_details(categories.get('security', {}))}
            
            <!-- Missing SEO Tags -->
            {self._generate_seo_details(categories.get('seo', {}))}
        </div>
        
        <div class="report-footer">
            <div class="footer-logo">Bejaa Digital Website Optimization Scanner</div>
            <div class="footer-info">
                Report generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}<br>
                Scanner Version: {self.results.get('scanner_version', '1.0.0')}<br>
                © 2024 Bejaa Digital. All rights reserved.
            </div>
        </div>
    </div>
    
    <button class="print-button" onclick="window.print()">
        <i class="fas fa-print"></i> Print Report
    </button>
    
    <script>
        // Add animation to score circles
        document.addEventListener('DOMContentLoaded', function() {{
            const scoreCircle = document.querySelector('.score-circle');
            const gradeCircle = document.querySelector('.grade-circle');
            
            // Animate on load
            setTimeout(() => {{
                scoreCircle.style.opacity = '1';
                gradeCircle.style.opacity = '1';
            }}, 500);
            
            // Add hover effects to category cards
            const categoryCards = document.querySelectorAll('.category-card');
            categoryCards.forEach(card => {{
                card.addEventListener('mouseenter', function() {{
                    this.style.transform = 'translateY(-5px)';
                }});
                card.addEventListener('mouseleave', function() {{
                    this.style.transform = 'translateY(0)';
                }});
            }});
        }});
    </script>
</body>
</html>
"""
        
        return html_content
    
    def _get_score_color(self, score):
        """Get color based on score"""
        if score >= 80:
            return "#28a745"  # Green
        elif score >= 60:
            return "#ffc107"  # Yellow
        elif score >= 40:
            return "#fd7e14"  # Orange
        else:
            return "#dc3545"  # Red
    
    def _get_grade_color(self, grade):
        """Get color based on grade"""
        grade_colors = {
            "A+": "#28a745", "A": "#28a745", "A-": "#5cb85c",
            "B+": "#17a2b8", "B": "#17a2b8", "B-": "#5bc0de",
            "C+": "#ffc107", "C": "#ffc107", "C-": "#f0ad4e",
            "D":  "#fd7e14", "F": "#dc3545"
        }
        return grade_colors.get(grade, "#dc3545")

    def _generate_category_cards(self, categories):
        """Generate HTML for category score cards"""
        cat_config = {
            "seo":           {"icon": "fas fa-search",          "title": "SEO"},
            "performance":   {"icon": "fas fa-bolt",            "title": "Performance"},
            "security":      {"icon": "fas fa-shield-alt",      "title": "Security"},
            "mobile":        {"icon": "fas fa-mobile-alt",      "title": "Mobile"},
            "accessibility": {"icon": "fas fa-universal-access","title": "Accessibility"},
            "technical_seo": {"icon": "fas fa-code",            "title": "Technical SEO"},
            "uiux":          {"icon": "fas fa-paint-brush",     "title": "UI/UX"},
        }

        cards = []
        for key, cfg in cat_config.items():
            data = categories.get(key, {})
            score = data.get("score", 0)
            color = self._get_score_color(score)

            if score >= 80:
                score_class = "score-excellent"
            elif score >= 60:
                score_class = "score-good"
            elif score >= 40:
                score_class = "score-fair"
            else:
                score_class = "score-poor"

            issues_html = ""
            issues = data.get("issues", [])[:3]
            if issues:
                li = "".join(f"<li>{html.escape(i)}</li>" for i in issues)
                issues_html = f'<div class="issues-list"><h4><i class="fas fa-exclamation-triangle"></i> Issues</h4><ul>{li}</ul></div>'

            recs = data.get("recommendations", [])[:2]
            recs_html = "".join(f'<p style="font-size:.85rem;color:#555;margin-top:6px">&#x2192; {html.escape(r)}</p>' for r in recs)

            cards.append(f"""
            <div class="category-card">
                <div class="category-header">
                    <div class="category-title">
                        <i class="{cfg['icon']}"></i>
                        <span>{cfg['title']}</span>
                    </div>
                    <span class="category-score {score_class}">{score}/100</span>
                </div>
                <div style="height:6px;background:#e0e0e0;border-radius:3px;margin:10px 0">
                    <div style="height:100%;width:{score}%;background:{color};border-radius:3px"></div>
                </div>
                <div class="category-details">{recs_html}</div>
                {issues_html}
            </div>""")

        return "\n".join(cards)

    def _generate_recommendations(self, recommendations):
        """Generate HTML recommendation cards"""
        if not recommendations:
            return '<div class="recommendation-card"><div class="recommendation-text"><h4>All good!</h4><p>No major recommendations at this time.</p></div></div>'

        cards = []
        icons = ["fas fa-search", "fas fa-bolt", "fas fa-shield-alt", "fas fa-mobile-alt", "fas fa-universal-access", "fas fa-code"]
        for i, rec in enumerate(recommendations[:9]):
            icon = icons[i % len(icons)]
            text = html.escape(rec.get("insight", rec) if isinstance(rec, dict) else rec)
            cards.append(f"""
            <div class="recommendation-card">
                <div class="recommendation-icon"><i class="{icon}"></i></div>
                <div class="recommendation-text"><p>{text}</p></div>
            </div>""")

        return "\n".join(cards)

    def _generate_security_details(self, security):
        """Generate security headers detail section"""
        if not security:
            return ""

        missing = security.get("headers_missing", [])
        present = security.get("headers_present", [])

        if not missing and not present:
            return ""

        present_html = "".join(
            f'<span style="background:#d4edda;color:#155724;padding:3px 10px;border-radius:4px;font-size:.8rem;margin:3px">{html.escape(h)}</span>'
            for h in present
        )
        missing_html = "".join(
            f'<span style="background:#f8d7da;color:#721c24;padding:3px 10px;border-radius:4px;font-size:.8rem;margin:3px">{html.escape(h)}</span>'
            for h in missing
        )

        return f"""
        <div class="section">
            <h2 class="section-title"><i class="fas fa-shield-alt"></i> Security Headers</h2>
            <div style="background:#f8f9fa;border-radius:12px;padding:20px">
                {'<div style="margin-bottom:12px"><strong style="color:#155724">Present:</strong><br>' + present_html + '</div>' if present else ''}
                {'<div><strong style="color:#721c24">Missing:</strong><br>' + missing_html + '</div>' if missing else ''}
            </div>
        </div>"""

    def _generate_seo_details(self, seo):
        """Generate SEO tags detail section"""
        if not seo:
            return ""

        present = seo.get("present_tags", [])
        missing = seo.get("missing_tags", [])

        if not present and not missing:
            return ""

        rows = "".join(
            f'<tr><td style="padding:6px 12px">{html.escape(t["tag"])}</td>'
            f'<td style="padding:6px 12px;color:#555;font-size:.85rem">{html.escape(str(t["content"])[:80])}</td>'
            f'<td style="padding:6px 12px"><span style="color:#28a745">&#x2713; Present</span></td></tr>'
            for t in present
        )
        rows += "".join(
            f'<tr><td style="padding:6px 12px">{html.escape(t)}</td>'
            f'<td style="padding:6px 12px;color:#999">—</td>'
            f'<td style="padding:6px 12px"><span style="color:#dc3545">&#x2717; Missing</span></td></tr>'
            for t in missing
        )

        return f"""
        <div class="section">
            <h2 class="section-title"><i class="fas fa-tags"></i> SEO Meta Tags</h2>
            <div style="overflow-x:auto">
                <table style="width:100%;border-collapse:collapse;background:#f8f9fa;border-radius:12px;overflow:hidden">
                    <thead>
                        <tr style="background:#e9ecef">
                            <th style="padding:10px 12px;text-align:left">Tag</th>
                            <th style="padding:10px 12px;text-align:left">Content</th>
                            <th style="padding:10px 12px;text-align:left">Status</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
        </div>"""


def generate_html_report(scan_results):
    """Standalone function — generates and saves HTML report, returns filename"""
    import os
    import re
    from datetime import datetime

    generator = ReportGenerator(scan_results)
    html_content = generator.generate_html_report()

    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = urlparse(scan_results.get("url", "unknown")).netloc
    domain_safe = re.sub(r"[^a-zA-Z0-9_-]", "_", domain)
    filename = f"{timestamp}_{domain_safe}.html"
    filepath = os.path.join("reports", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    return filename