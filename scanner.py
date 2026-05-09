#!/usr/bin/env python3
"""
Bejaa Digital Website Optimization Scanner
Enhanced Version - Production Ready
"""

import sys
import json
import time
import os
import re
import ssl
import socket
import urllib3
from datetime import datetime
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

from config import SCANNER_CONFIG, SECURITY_HEADERS, SEO_TAGS, PERFORMANCE_METRICS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WebsiteScanner:

    def __init__(self, url):
        self.url = self.normalize_url(url)
        self.domain = urlparse(self.url).netloc
        self.results = {
            "url": self.url,
            "domain": self.domain,
            "scan_date": datetime.now().isoformat(),
            "scanner_version": SCANNER_CONFIG["version"],
            "overall_score": 0,
            "grade": "F",
            "categories": {},
            "detailed_analysis": {},
            "actionable_insights": [],
            "priority_fixes": [],
            "category_scores": {},
            "error": None
        }

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.session.verify = False
        self.session.timeout = SCANNER_CONFIG["timeouts"]["request_timeout"]

    @staticmethod
    def calculate_grade(score):
        if score >= 90: return "A+"
        elif score >= 85: return "A"
        elif score >= 80: return "A-"
        elif score >= 75: return "B+"
        elif score >= 70: return "B"
        elif score >= 65: return "B-"
        elif score >= 60: return "C+"
        elif score >= 55: return "C"
        elif score >= 50: return "C-"
        elif score >= 40: return "D"
        else: return "F"

    def normalize_url(self, url):
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url.rstrip("/")

    def run_full_scan(self):
        print(f"Scanning {self.url}...")

        try:
            if not self.check_connectivity():
                error = self.results.get("connectivity", {}).get("error", "Unknown error")
                print(f"Website not accessible: {error}")
                return False

            self.check_seo()
            self.check_performance()
            self.check_security()
            self.check_mobile()
            self.check_accessibility()
            self.check_technical_seo()
            self.check_uiux()

            self.calculate_overall_score()
            self.generate_detailed_analysis()
            self.generate_actionable_insights()
            self.identify_priority_fixes()

            self.results["grade"] = self.calculate_grade(self.results["overall_score"])

            print(f"Scan complete — Score: {self.results['overall_score']}/100 | Grade: {self.results['grade']} | Priority fixes: {len(self.results['priority_fixes'])}")
            return True

        except Exception as e:
            self.results["error"] = f"Scan error: {str(e)}"
            print(f"Error: {self.results['error']}")
            return False

    # ─── CONNECTIVITY ────────────────────────────────────────────────────────────

    def check_connectivity(self):
        try:
            start_time = time.time()
            response = self.session.get(
                self.url,
                timeout=SCANNER_CONFIG["timeouts"]["request_timeout"],
                allow_redirects=True,
                stream=True
            )

            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > 2097152:  # 2MB cap
                    break

            response_time = time.time() - start_time

            self.results["connectivity"] = {
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "final_url": response.url,
                "accessible": response.status_code == 200,
                "content_length": len(content),
                "server": response.headers.get("Server", "Unknown"),
                "content_type": response.headers.get("Content-Type", "Unknown"),
                "redirects": len(response.history)
            }

            self.results["response_headers"] = dict(response.headers)

            try:
                self.results["html_content"] = content.decode("utf-8", errors="ignore")
            except Exception:
                self.results["html_content"] = content.decode("latin-1", errors="ignore")

            # Accept any 2xx response as accessible
            return 200 <= response.status_code < 300

        except requests.exceptions.Timeout:
            self.results["connectivity"] = {"error": "Connection timeout", "accessible": False, "timeout": True}
            return False
        except requests.exceptions.SSLError:
            self.results["connectivity"] = {"error": "SSL certificate error", "accessible": False, "ssl_error": True}
            return False
        except requests.exceptions.ConnectionError:
            self.results["connectivity"] = {"error": "Connection failed — site may be down", "accessible": False, "connection_error": True}
            return False
        except requests.RequestException as e:
            self.results["connectivity"] = {"error": str(e), "accessible": False}
            return False

    # ─── SEO ─────────────────────────────────────────────────────────────────────

    def check_seo(self):
        print("  Checking SEO...")

        seo = {
            "score": 0,
            "checks": {},
            "missing_tags": [],
            "present_tags": [],
            "issues": [],
            "warnings": [],
            "recommendations": []
        }

        if "html_content" not in self.results:
            seo["score"] = 0
            self.results["categories"]["seo"] = seo
            return

        soup = BeautifulSoup(self.results["html_content"], "html.parser")

        for tag in SEO_TAGS:
            if tag.startswith("og:") or tag.startswith("twitter:"):
                meta = soup.find("meta", property=tag)
            elif tag == "title":
                meta = soup.find("title")
            else:
                meta = soup.find("meta", attrs={"name": tag})

            if meta:
                content = meta.text.strip() if tag == "title" else meta.get("content", "").strip()
                if tag == "title":
                    if len(content) < 30:
                        seo["warnings"].append(f"Title too short ({len(content)} chars — min 30)")
                    elif len(content) > 60:
                        seo["warnings"].append(f"Title too long ({len(content)} chars — max 60)")
                if tag == "description" and content:
                    if len(content) < 120:
                        seo["warnings"].append(f"Meta description too short ({len(content)} chars — min 120)")
                    elif len(content) > 160:
                        seo["warnings"].append(f"Meta description too long ({len(content)} chars — max 160)")

                seo["present_tags"].append({
                    "tag": tag,
                    "content": content[:150] + "..." if len(content) > 150 else content,
                    "length": len(content)
                })
            else:
                seo["missing_tags"].append(tag)
                seo["issues"].append(f"Missing {tag} tag")

        # Headings
        headings = {f"h{i}": len(soup.find_all(f"h{i}")) for i in range(1, 7)}
        seo["checks"]["headings"] = headings

        if headings.get("h1", 0) == 0:
            seo["issues"].append("No H1 heading found")
        elif headings.get("h1", 0) > 1:
            seo["warnings"].append(f"Multiple H1 headings ({headings['h1']}) — use only one")

        # Images
        images = soup.find_all("img")
        missing_alt = sum(1 for img in images if not img.get("alt"))
        seo["checks"]["images"] = {
            "total": len(images),
            "with_alt": len(images) - missing_alt,
            "without_alt": missing_alt
        }
        if missing_alt > 0:
            seo["issues"].append(f"{missing_alt} images missing alt text")

        # Links
        all_links = soup.find_all("a", href=True)
        internal = [l for l in all_links if not l["href"].startswith("http") or self.domain in l["href"]]
        external = [l for l in all_links if l["href"].startswith("http") and self.domain not in l["href"]]
        seo["checks"]["links"] = {
            "total": len(all_links),
            "internal": len(internal),
            "external": len(external)
        }

        # Score
        base = int((len(seo["present_tags"]) / len(SEO_TAGS)) * 100) if SEO_TAGS else 0
        bonus = 0
        if (len(images) - missing_alt) > 0: bonus += 5
        if headings.get("h1", 0) == 1: bonus += 10
        if len(internal) > 5: bonus += 5

        penalty = len(seo["issues"]) * 5 + len(seo["warnings"]) * 2
        seo["score"] = max(0, min(100, base + bonus - penalty))

        if seo["missing_tags"]:
            seo["recommendations"].append(f"Add missing meta tags: {', '.join(seo['missing_tags'][:5])}")
        if missing_alt > 0:
            seo["recommendations"].append(f"Add alt text to {missing_alt} images for SEO and accessibility")
        if headings.get("h1", 0) == 0:
            seo["recommendations"].append("Add an H1 heading — it's a strong Google ranking signal")

        self.results["categories"]["seo"] = seo

    # ─── PERFORMANCE ─────────────────────────────────────────────────────────────

    def check_performance(self):
        print("  Checking performance...")

        perf = {
            "score": 0,
            "metrics": {},
            "issues": [],
            "warnings": [],
            "recommendations": []
        }

        try:
            start = time.time()
            response = self.session.get(self.url, timeout=SCANNER_CONFIG["timeouts"]["request_timeout"], stream=True)

            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > 65536:
                    break

            load_time = time.time() - start
            page_size_kb = len(content) / 1024

            perf["metrics"]["page_load_time"] = round(load_time, 3)
            perf["metrics"]["page_size_kb"] = round(page_size_kb, 2)

            # Compression
            encoding = response.headers.get("Content-Encoding", "")
            perf["metrics"]["compression"] = encoding or "None"
            if not encoding:
                perf["warnings"].append("No gzip/Brotli compression — enable on server for faster delivery")

            # Cache headers
            cache = response.headers.get("Cache-Control", "")
            perf["metrics"]["cache_control"] = cache or "Not set"
            if not cache:
                perf["warnings"].append("No Cache-Control header — browsers can't cache static assets")

            soup = BeautifulSoup(content.decode("utf-8", errors="ignore"), "html.parser")

            resources = {
                "images": len(soup.find_all("img")),
                "scripts": len(soup.find_all("script")),
                "stylesheets": len(soup.find_all("link", rel="stylesheet")),
                "iframes": len(soup.find_all("iframe"))
            }
            perf["metrics"]["resources"] = resources

            render_blocking = sum(
                1 for s in soup.find_all("script", src=True)
                if not s.get("async") and not s.get("defer")
            )
            perf["metrics"]["render_blocking_scripts"] = render_blocking

            lazy_images = sum(1 for img in soup.find_all("img") if img.get("loading") == "lazy")
            perf["metrics"]["lazy_loaded_images"] = lazy_images

            # Score
            score = 100

            if load_time > 3.0:
                score -= min(40, int((load_time - 3.0) * 15))
                perf["issues"].append(f"Very slow load time: {load_time:.2f}s (target: <2s)")
            elif load_time > 2.0:
                score -= min(20, int((load_time - 2.0) * 10))
                perf["warnings"].append(f"Load time could be improved: {load_time:.2f}s")

            if page_size_kb > 2000:
                score -= min(30, int((page_size_kb - 2000) / 100))
                perf["issues"].append(f"Page too large: {page_size_kb:.0f}KB (target: <1000KB)")
            elif page_size_kb > 1000:
                score -= 10
                perf["warnings"].append(f"Large page size: {page_size_kb:.0f}KB")

            total_res = sum(resources.values())
            if total_res > 100:
                score -= min(25, int((total_res - 100) / 5))
                perf["issues"].append(f"Too many HTTP requests: {total_res} (target: <50)")
            elif total_res > 50:
                score -= 10
                perf["warnings"].append(f"High request count: {total_res}")

            if render_blocking > 3:
                score -= min(20, render_blocking * 3)
                perf["issues"].append(f"{render_blocking} render-blocking scripts slowing page paint")
            elif render_blocking > 0:
                score -= render_blocking * 2
                perf["warnings"].append(f"{render_blocking} scripts without async/defer")

            if not encoding:
                score -= 10
            if not cache:
                score -= 5

            perf["score"] = max(0, score)

            if load_time > 2.0:
                perf["recommendations"].append("Use a CDN and enable server-side caching to cut load time")
            if page_size_kb > 1000:
                perf["recommendations"].append("Compress and resize images — use WebP format where possible")
            if render_blocking > 0:
                perf["recommendations"].append(f"Add async or defer to {render_blocking} render-blocking <script> tags")
            if resources["images"] > 20 and lazy_images == 0:
                perf["recommendations"].append("Add loading='lazy' to images below the fold")
            if not encoding:
                perf["recommendations"].append("Enable gzip or Brotli compression on your web server")
            if not cache:
                perf["recommendations"].append("Set Cache-Control headers for static assets (images, CSS, JS)")

        except Exception as e:
            perf["error"] = str(e)
            perf["score"] = 0

        self.results["categories"]["performance"] = perf

    # ─── SECURITY ────────────────────────────────────────────────────────────────

    def check_security(self):
        print("  Checking security...")

        sec = {
            "score": 0,
            "checks": {},
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "headers_present": [],
            "headers_missing": []
        }

        headers = {k.lower(): v for k, v in self.results.get("response_headers", {}).items()}

        # Security headers
        for header in SECURITY_HEADERS:
            if header.lower() in headers:
                sec["headers_present"].append(header)
            else:
                sec["headers_missing"].append(header)
                sec["issues"].append(f"Missing: {header}")

        # HTTPS
        is_https = self.url.startswith("https://")
        sec["checks"]["https"] = is_https
        if not is_https:
            sec["issues"].append("Site not using HTTPS — data transmitted unencrypted")

        # HTTP → HTTPS redirect
        if is_https:
            try:
                http_url = self.url.replace("https://", "http://")
                r = self.session.get(http_url, timeout=5, allow_redirects=True)
                redirects_ok = r.url.startswith("https://")
                sec["checks"]["https_redirect"] = redirects_ok
                if not redirects_ok:
                    sec["warnings"].append("HTTP does not redirect to HTTPS")
            except Exception:
                sec["checks"]["https_redirect"] = None

        # SSL certificate
        if is_https:
            try:
                parsed = urlparse(self.url)
                ctx = ssl.create_default_context()
                conn = ctx.wrap_socket(
                    socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                    server_hostname=parsed.netloc
                )
                conn.settimeout(SCANNER_CONFIG["timeouts"]["ssl_timeout"])
                conn.connect((parsed.netloc, 443))
                cert = conn.getpeercert()
                conn.close()

                not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                days_left = (not_after - datetime.now()).days
                sec["checks"]["ssl_cert"] = {
                    "valid": True,
                    "expires": cert["notAfter"],
                    "days_remaining": days_left
                }
                if days_left < 30:
                    sec["issues"].append(f"SSL certificate expires in {days_left} days — renew immediately")
                elif days_left < 90:
                    sec["warnings"].append(f"SSL certificate expires in {days_left} days — plan renewal")
            except ssl.SSLCertVerificationError:
                sec["checks"]["ssl_cert"] = {"valid": False, "error": "Certificate verification failed"}
                sec["issues"].append("SSL certificate is invalid or untrusted")
            except Exception as e:
                sec["checks"]["ssl_cert"] = {"valid": None, "error": str(e)}

        # Server header info leakage
        server_val = headers.get("server", "")
        powered_by = headers.get("x-powered-by", "")
        sec["checks"]["server_info_leak"] = bool(server_val or powered_by)
        if server_val:
            sec["warnings"].append(f"Server header reveals technology: {server_val}")
        if powered_by:
            sec["warnings"].append(f"X-Powered-By exposes stack: {powered_by}")

        # Mixed content
        if "html_content" in self.results and is_https:
            mixed = re.findall(r'src=["\']http://[^"\']+["\']', self.results["html_content"])
            sec["checks"]["mixed_content"] = len(mixed)
            if mixed:
                sec["issues"].append(f"Mixed content: {len(mixed)} HTTP resources on HTTPS page")
        else:
            sec["checks"]["mixed_content"] = 0

        # Score
        header_score = (len(sec["headers_present"]) / len(SECURITY_HEADERS)) * 50 if SECURITY_HEADERS else 0
        https_bonus = 30 if is_https else 0
        cert_valid = sec.get("checks", {}).get("ssl_cert", {}).get("valid")
        cert_bonus = 20 if cert_valid else 0
        penalty = len(sec["issues"]) * 5 + len(sec["warnings"]) * 2

        sec["score"] = max(0, min(100, int(header_score + https_bonus + cert_bonus - penalty)))

        if sec["headers_missing"]:
            sec["recommendations"].append(f"Add security headers: {', '.join(sec['headers_missing'][:3])}")
        if not is_https:
            sec["recommendations"].append("Install SSL certificate and force HTTPS for all traffic")
        if powered_by:
            sec["recommendations"].append("Remove X-Powered-By header to hide your tech stack from attackers")
        if sec["checks"].get("mixed_content", 0) > 0:
            sec["recommendations"].append("Fix mixed content: update all HTTP resource URLs to HTTPS")

        self.results["categories"]["security"] = sec

    # ─── MOBILE ──────────────────────────────────────────────────────────────────

    def check_mobile(self):
        print("  Checking mobile...")

        mob = {
            "score": 0,
            "checks": {},
            "issues": [],
            "warnings": [],
            "recommendations": []
        }

        if "html_content" not in self.results:
            self.results["categories"]["mobile"] = mob
            return

        soup = BeautifulSoup(self.results["html_content"], "html.parser")
        score = 100

        # Viewport
        viewport = soup.find("meta", attrs={"name": "viewport"})
        mob["checks"]["viewport"] = bool(viewport)
        if viewport:
            vp_content = viewport.get("content", "")
            mob["checks"]["viewport_content"] = vp_content
            if "width=device-width" not in vp_content:
                mob["warnings"].append("Viewport missing width=device-width")
                score -= 10
            if "initial-scale=1" not in vp_content:
                mob["warnings"].append("Viewport missing initial-scale=1")
                score -= 5
        else:
            mob["issues"].append("No viewport meta tag — site will not scale on mobile")
            score -= 40

        # Media queries
        has_media_queries = any(
            "@media" in tag.get_text()
            for tag in soup.find_all("style")
        ) or bool(soup.find_all("link", rel="stylesheet", media=True))
        mob["checks"]["responsive_css"] = has_media_queries
        if not has_media_queries:
            mob["warnings"].append("No CSS media queries detected — layout may break on small screens")
            score -= 25

        # Fixed-width elements (risk of horizontal scroll)
        fixed_width_count = len(re.findall(r"width:\s*[0-9]{4,}px", self.results["html_content"]))
        mob["checks"]["large_fixed_width_elements"] = fixed_width_count
        if fixed_width_count > 0:
            mob["warnings"].append(f"{fixed_width_count} large fixed-width elements detected (may cause horizontal scroll)")
            score -= min(15, fixed_width_count * 3)

        # Responsive images
        images = soup.find_all("img")
        responsive_imgs = sum(1 for img in images if img.get("srcset") or img.get("sizes"))
        mob["checks"]["images"] = {
            "total": len(images),
            "responsive": responsive_imgs
        }
        if len(images) > 0 and responsive_imgs == 0:
            mob["warnings"].append("No responsive images (srcset) found — serving oversized images on mobile")
            score -= 10

        # Touch icon
        touch_icon = soup.find("link", rel=lambda r: isinstance(r, list) and "apple-touch-icon" in r)
        mob["checks"]["touch_icon"] = bool(touch_icon)

        mob["score"] = max(0, score - len(mob["issues"]) * 5)

        if not mob["checks"]["viewport"]:
            mob["recommendations"].append('Add <meta name="viewport" content="width=device-width, initial-scale=1"> to <head>')
        if not has_media_queries:
            mob["recommendations"].append("Implement responsive CSS with mobile-first media queries")
        if responsive_imgs == 0 and len(images) > 0:
            mob["recommendations"].append("Use srcset on images to serve correct sizes per screen resolution")

        self.results["categories"]["mobile"] = mob

    # ─── ACCESSIBILITY ───────────────────────────────────────────────────────────

    def check_accessibility(self):
        print("  Checking accessibility...")

        a11y = {
            "score": 0,
            "checks": {},
            "issues": [],
            "warnings": [],
            "recommendations": []
        }

        if "html_content" not in self.results:
            self.results["categories"]["accessibility"] = a11y
            return

        soup = BeautifulSoup(self.results["html_content"], "html.parser")
        score = 100

        # Lang attribute
        html_tag = soup.find("html")
        has_lang = bool(html_tag and html_tag.get("lang"))
        a11y["checks"]["lang_attribute"] = has_lang
        if not has_lang:
            a11y["issues"].append("Missing lang attribute on <html> — screen readers need this")
            score -= 10

        # Images alt text
        images = soup.find_all("img")
        missing_alt = sum(1 for img in images if img.get("alt") is None)
        a11y["checks"]["images"] = {
            "total": len(images),
            "with_alt": len(images) - missing_alt,
            "missing_alt": missing_alt
        }
        if missing_alt > 0:
            a11y["issues"].append(f"{missing_alt} images missing alt attribute")
            score -= min(20, missing_alt * 3)

        # Form labels
        inputs = soup.find_all("input", type=lambda t: t not in ["hidden", "submit", "button", "reset"])
        unlabeled = 0
        for inp in inputs:
            inp_id = inp.get("id")
            has_label = bool(inp_id and soup.find("label", attrs={"for": inp_id}))
            has_aria = bool(inp.get("aria-label") or inp.get("aria-labelledby"))
            if not has_label and not has_aria:
                unlabeled += 1

        a11y["checks"]["form_labels"] = {
            "total_inputs": len(inputs),
            "unlabeled": unlabeled
        }
        if unlabeled > 0:
            a11y["issues"].append(f"{unlabeled} form inputs missing accessible labels")
            score -= min(15, unlabeled * 5)

        # Semantic landmarks
        landmarks = {
            "main": bool(soup.find("main") or soup.find(attrs={"role": "main"})),
            "nav": bool(soup.find("nav") or soup.find(attrs={"role": "navigation"})),
            "header": bool(soup.find("header") or soup.find(attrs={"role": "banner"})),
            "footer": bool(soup.find("footer") or soup.find(attrs={"role": "contentinfo"}))
        }
        a11y["checks"]["landmarks"] = landmarks
        missing_landmarks = [k for k, v in landmarks.items() if not v]
        if missing_landmarks:
            a11y["warnings"].append(f"Missing semantic HTML5 landmarks: {', '.join(missing_landmarks)}")
            score -= len(missing_landmarks) * 3

        # Empty buttons
        buttons = soup.find_all("button")
        empty_buttons = sum(1 for b in buttons if not b.get_text(strip=True) and not b.get("aria-label"))
        a11y["checks"]["empty_buttons"] = empty_buttons
        if empty_buttons > 0:
            a11y["issues"].append(f"{empty_buttons} buttons with no text or aria-label")
            score -= min(10, empty_buttons * 3)

        # Skip nav link
        skip_link = (
            soup.find("a", href="#main") or
            soup.find("a", href="#content") or
            soup.find("a", string=re.compile(r"skip", re.I))
        )
        a11y["checks"]["skip_nav"] = bool(skip_link)
        if not skip_link:
            a11y["warnings"].append("No skip navigation link — keyboard users can't bypass repeated nav")
            score -= 5

        a11y["score"] = max(0, score)

        if not has_lang:
            a11y["recommendations"].append('Add lang attribute to <html> (e.g. <html lang="en">)')
        if missing_alt > 0:
            a11y["recommendations"].append(f"Add descriptive alt text to {missing_alt} images")
        if unlabeled > 0:
            a11y["recommendations"].append("Associate <label for='id'> with every form input")
        if missing_landmarks:
            a11y["recommendations"].append(f"Add semantic elements: <{missing_landmarks[0]}>, etc.")

        self.results["categories"]["accessibility"] = a11y

    # ─── TECHNICAL SEO ───────────────────────────────────────────────────────────

    def check_technical_seo(self):
        print("  Checking technical SEO...")

        tech = {
            "score": 0,
            "checks": {},
            "issues": [],
            "warnings": [],
            "recommendations": []
        }

        score = 100
        parsed = urlparse(self.url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        # robots.txt
        try:
            r = self.session.get(f"{base}/robots.txt", timeout=5)
            has_robots = r.status_code == 200 and len(r.text.strip()) > 0
            tech["checks"]["robots_txt"] = {"exists": has_robots, "status_code": r.status_code}
            if not has_robots:
                tech["warnings"].append("No robots.txt found")
                score -= 10
        except Exception:
            tech["checks"]["robots_txt"] = {"exists": False}
            score -= 10

        # sitemap.xml
        try:
            r = self.session.get(f"{base}/sitemap.xml", timeout=5)
            has_sitemap = r.status_code == 200 and ("<urlset" in r.text or "<sitemapindex" in r.text)
            tech["checks"]["sitemap_xml"] = {"exists": has_sitemap, "status_code": r.status_code}
            if not has_sitemap:
                tech["warnings"].append("No sitemap.xml found")
                score -= 10
        except Exception:
            tech["checks"]["sitemap_xml"] = {"exists": False}
            score -= 10

        if "html_content" in self.results:
            soup = BeautifulSoup(self.results["html_content"], "html.parser")

            # Canonical
            canonical = soup.find("link", rel="canonical")
            tech["checks"]["canonical"] = bool(canonical)
            if not canonical:
                tech["warnings"].append("No canonical URL tag — duplicate content risk")
                score -= 10

            # Structured data (JSON-LD)
            schema_scripts = soup.find_all("script", type="application/ld+json")
            tech["checks"]["structured_data"] = {
                "present": bool(schema_scripts),
                "count": len(schema_scripts)
            }
            if not schema_scripts:
                tech["warnings"].append("No JSON-LD structured data — missing rich snippet eligibility")
                score -= 10

            # Open Graph completeness
            og_title = soup.find("meta", property="og:title")
            og_desc = soup.find("meta", property="og:description")
            og_image = soup.find("meta", property="og:image")
            og_complete = all([og_title, og_desc, og_image])
            tech["checks"]["open_graph"] = {
                "complete": og_complete,
                "has_title": bool(og_title),
                "has_description": bool(og_desc),
                "has_image": bool(og_image)
            }
            if not og_complete:
                missing_og = [k for k, v in [("og:title", og_title), ("og:description", og_desc), ("og:image", og_image)] if not v]
                tech["warnings"].append(f"Incomplete Open Graph: missing {', '.join(missing_og)}")
                score -= 5

            # Favicon
            favicon = (
                soup.find("link", rel="icon") or
                soup.find("link", rel="shortcut icon") or
                soup.find("link", rel=lambda r: isinstance(r, list) and "apple-touch-icon" in r)
            )
            tech["checks"]["favicon"] = bool(favicon)
            if not favicon:
                tech["warnings"].append("No favicon detected")
                score -= 5

            # Inline scripts count
            inline_scripts = len([s for s in soup.find_all("script") if not s.get("src") and s.get_text(strip=True)])
            tech["checks"]["inline_scripts"] = inline_scripts
            if inline_scripts > 5:
                tech["warnings"].append(f"{inline_scripts} inline scripts — externalize for better caching")

        tech["score"] = max(0, score)

        if not tech["checks"].get("robots_txt", {}).get("exists"):
            tech["recommendations"].append("Create robots.txt to control how search engines crawl your site")
        if not tech["checks"].get("sitemap_xml", {}).get("exists"):
            tech["recommendations"].append("Create sitemap.xml and submit to Google Search Console")
        if not tech["checks"].get("canonical"):
            tech["recommendations"].append("Add <link rel='canonical' href='...'> to prevent duplicate content")
        if not tech["checks"].get("structured_data", {}).get("present"):
            tech["recommendations"].append("Add JSON-LD Schema.org markup for richer Google search results")

        self.results["categories"]["technical_seo"] = tech

    # ─── UI/UX ───────────────────────────────────────────────────────────────────

    def check_uiux(self):
        print("  Checking UI/UX...")

        uiux = {
            "score": 0,
            "checks": {},
            "issues": [],
            "warnings": [],
            "recommendations": []
        }

        if "html_content" not in self.results:
            self.results["categories"]["uiux"] = uiux
            return

        soup = BeautifulSoup(self.results["html_content"], "html.parser")
        html_raw = self.results["html_content"]
        score = 100

        # 1. CTA buttons
        cta_pattern = re.compile(
            r'\b(get|start|try|buy|order|book|contact|sign\s*up|register|download|'
            r'learn more|discover|explore|request|apply|subscribe|free|consult|quote)\b',
            re.I
        )
        clickable = soup.find_all(["button", "a"])
        cta_count = sum(1 for el in clickable if el.get_text(strip=True) and cta_pattern.search(el.get_text(strip=True)))
        uiux["checks"]["cta_buttons"] = cta_count
        if cta_count == 0:
            uiux["issues"].append("No clear CTA buttons found — visitors don't know what action to take")
            score -= 20
        elif cta_count < 2:
            uiux["warnings"].append("Only 1 CTA button — add more conversion points throughout the page")
            score -= 5

        # 2. Navigation clarity
        nav = soup.find("nav")
        nav_link_count = len(nav.find_all("a")) if nav else 0
        uiux["checks"]["nav_links"] = nav_link_count
        if not nav:
            uiux["warnings"].append("No <nav> element — users can't easily navigate the site")
            score -= 10
        elif nav_link_count > 8:
            uiux["warnings"].append(f"Navigation has {nav_link_count} items — too many choices hurt conversion (aim for 5-7)")
            score -= 8

        # 3. Trust signals
        all_hrefs = [a.get("href", "").lower() for a in soup.find_all("a", href=True)]
        html_lower = html_raw.lower()
        trust = {
            "contact_link": any("contact" in h for h in all_hrefs),
            "about_link": any("about" in h for h in all_hrefs),
            "privacy_link": any("privacy" in h for h in all_hrefs),
            "phone_number": bool(re.search(r'(\+?6?01[0-9][\s\-]?[0-9]{7,8}|\+?[0-9]{2,4}[\s\-][0-9]{6,10})', html_lower)),
        }
        uiux["checks"]["trust_signals"] = trust
        missing_trust = [k for k, v in trust.items() if not v]
        if len(missing_trust) >= 3:
            uiux["issues"].append(f"Missing trust signals: {', '.join(missing_trust)}")
            score -= 15
        elif missing_trust:
            uiux["warnings"].append(f"Some trust signals missing: {', '.join(missing_trust)}")
            score -= 5

        # 4. Social proof
        has_social_proof = bool(re.search(
            r'\b(testimonial|review|client|customer|partner|trusted by|rated|award|certif|case study)\b',
            html_raw, re.I
        ))
        uiux["checks"]["social_proof"] = has_social_proof
        if not has_social_proof:
            uiux["warnings"].append("No social proof detected — testimonials and client logos build trust")
            score -= 10

        # 5. Hero / above-fold value proposition
        has_hero = bool(
            soup.find(class_=re.compile(r'hero|banner|jumbotron|masthead', re.I)) or
            soup.find(id=re.compile(r'hero|banner', re.I))
        )
        has_h1 = bool(soup.find("h1"))
        uiux["checks"]["hero_section"] = has_hero
        uiux["checks"]["has_h1"] = has_h1
        if not has_hero and not has_h1:
            uiux["issues"].append("No hero section or H1 — visitors can't tell what the site offers in 3 seconds")
            score -= 15
        elif not has_hero:
            uiux["warnings"].append("No hero section — add a clear value proposition banner above the fold")
            score -= 5

        # 6. Footer completeness
        footer = soup.find("footer")
        footer_links = len(footer.find_all("a")) if footer else 0
        uiux["checks"]["footer_links"] = footer_links
        if not footer:
            uiux["warnings"].append("No <footer> element — add contact info, links, and copyright")
            score -= 5
        elif footer_links < 3:
            uiux["warnings"].append("Sparse footer — add contact, social links, and key navigation")
            score -= 3

        # 7. Tiny/unreadable inline text
        tiny_text = len(re.findall(r'font-size\s*:\s*[1-9]px', html_raw))
        uiux["checks"]["tiny_text_count"] = tiny_text
        if tiny_text > 0:
            uiux["warnings"].append(f"{tiny_text} elements with font-size under 10px — unreadable on any device")
            score -= min(10, tiny_text * 3)

        # 8. Dead/placeholder links
        dead_links = sum(
            1 for a in soup.find_all("a", href=True)
            if a["href"].strip() in ["#", "", "javascript:void(0)", "javascript:"]
        )
        uiux["checks"]["placeholder_links"] = dead_links
        if dead_links > 3:
            uiux["warnings"].append(f"{dead_links} placeholder links (href='#') — replace with real destinations")
            score -= min(10, dead_links * 2)

        # 9. Modernity signals
        uses_custom_props = "var(--" in html_raw
        uses_google_fonts = "fonts.googleapis.com" in html_raw
        uses_framework = bool(re.search(r'bootstrap|tailwind|bulma|foundation', html_raw, re.I))
        uiux["checks"]["modernity"] = {
            "css_custom_properties": uses_custom_props,
            "custom_fonts": uses_google_fonts,
            "css_framework": uses_framework,
        }
        if not any([uses_custom_props, uses_google_fonts, uses_framework]):
            uiux["warnings"].append("No modern CSS patterns detected — design may look dated")
            score -= 8

        # 10. Cookie / GDPR notice
        has_cookie = bool(re.search(r'\b(cookie|gdpr|consent)\b', html_raw, re.I))
        uiux["checks"]["cookie_notice"] = has_cookie
        if not has_cookie:
            uiux["warnings"].append("No cookie consent notice — required for EU visitors, builds compliance trust")
            score -= 4

        uiux["score"] = max(0, score)

        if cta_count == 0:
            uiux["recommendations"].append("Add prominent CTAs ('Get a Quote', 'Contact Us', 'Book Now') above the fold and after key sections")
        if not has_social_proof:
            uiux["recommendations"].append("Add testimonials or client logos — social proof increases conversion by up to 34%")
        if not has_hero:
            uiux["recommendations"].append("Design a hero section with a clear headline, subtext, and one strong CTA button")
        if not trust.get("phone_number"):
            uiux["recommendations"].append("Display your phone number prominently — it dramatically increases visitor trust")
        if not has_cookie:
            uiux["recommendations"].append("Add a GDPR cookie consent banner for legal compliance")
        if not any([uses_custom_props, uses_google_fonts, uses_framework]):
            uiux["recommendations"].append("Use modern CSS (custom properties, Google Fonts, or a CSS framework) for a polished look")

        self.results["categories"]["uiux"] = uiux

    # ─── SCORING & ANALYSIS ──────────────────────────────────────────────────────

    def calculate_overall_score(self):
        categories = self.results["categories"]

        # Weighted scoring — all 6 categories contribute
        weight_map = {
            "seo": 0.18,
            "performance": 0.22,
            "security": 0.18,
            "mobile": 0.13,
            "accessibility": 0.08,
            "technical_seo": 0.09,
            "uiux": 0.12
        }

        total_weight = 0
        weighted_sum = 0

        for cat, weight in weight_map.items():
            if cat in categories and "score" in categories[cat]:
                weighted_sum += categories[cat]["score"] * weight
                total_weight += weight

        if total_weight > 0:
            overall = weighted_sum / total_weight
        else:
            overall = 0

        self.results["overall_score"] = round(overall)
        self.results["category_scores"] = {
            cat: categories[cat]["score"]
            for cat in weight_map
            if cat in categories and "score" in categories[cat]
        }

    def generate_detailed_analysis(self):
        analysis = {}
        for cat_name, cat_data in self.results["categories"].items():
            score = cat_data.get("score", 0)
            analysis[cat_name] = {
                "score": score,
                "status": "good" if score >= 80 else ("needs_improvement" if score >= 50 else "poor"),
                "issue_count": len(cat_data.get("issues", [])),
                "warning_count": len(cat_data.get("warnings", [])),
                "top_issues": cat_data.get("issues", [])[:3],
                "top_recommendations": cat_data.get("recommendations", [])[:3]
            }
        self.results["detailed_analysis"] = analysis

    def generate_actionable_insights(self):
        priority_order = {"high": 0, "medium": 1, "low": 2}
        insights = []

        for cat_name, cat_data in self.results["categories"].items():
            score = cat_data.get("score", 0)
            priority = "high" if score < 50 else ("medium" if score < 75 else "low")
            for rec in cat_data.get("recommendations", []):
                insights.append({
                    "category": cat_name,
                    "priority": priority,
                    "insight": rec,
                    "score": score
                })

        insights.sort(key=lambda x: (priority_order[x["priority"]], x["score"]))
        self.results["actionable_insights"] = insights

    def identify_priority_fixes(self):
        fixes = []
        for cat_name, cat_data in self.results["categories"].items():
            score = cat_data.get("score", 100)
            for issue in cat_data.get("issues", []):
                fixes.append({
                    "category": cat_name,
                    "issue": issue,
                    "severity": "critical" if score < 50 else "major"
                })

        fixes.sort(key=lambda x: 0 if x["severity"] == "critical" else 1)
        self.results["priority_fixes"] = fixes[:15]

    # ─── SAVE ────────────────────────────────────────────────────────────────────

    def save_results(self, format="json"):
        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain_safe = re.sub(r"[^a-zA-Z0-9_-]", "_", self.domain)

        if format == "json":
            filename = f"{timestamp}_{domain_safe}.json"
            filepath = os.path.join("reports", filename)
            exportable = {k: v for k, v in self.results.items() if k not in ["html_content", "response_headers"]}
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(exportable, f, indent=2, default=str)
            return filename

        return None


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://bejaadigital.com"
    scanner = WebsiteScanner(target)
    if scanner.run_full_scan():
        filename = scanner.save_results(format="json")
        print(f"\nReport saved: reports/{filename}")
        print(json.dumps(scanner.results["category_scores"], indent=2))
