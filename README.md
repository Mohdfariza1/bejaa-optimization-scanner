# 🚀 Bejaa Digital Website Optimization Scanner

A professional website optimization scanner tool to build trust with prospects and generate leads for Bejaa Digital.

## 🎯 Features

- **SEO Analysis**: Meta tags, headings, image optimization
- **Performance Check**: Page speed, resource optimization
- **Security Scan**: SSL, security headers, vulnerabilities
- **Mobile Optimization**: Responsive design, touch compatibility
- **Professional Reports**: PDF generation with actionable recommendations
- **Lead Capture**: Integrated with Bejaa Digital services

## 📦 Installation

### 1. Clone/Download
```bash
git clone [repository-url]
cd bejaa-optimization-scanner
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Scanner

**Option A: Web Interface (Recommended for Prospects)**
```bash
python app.py
```
Then open: http://localhost:5000

**Option B: Command Line (For Technical Users)**
```bash
python scanner.py https://example.com
```

## 🛠️ Usage

### Web Interface
1. Visit http://localhost:5000
2. Enter website URL
3. Click "Scan Website"
4. View detailed report with scores and recommendations
5. Download PDF report or request consultation

### Command Line
```bash
# Basic scan
python scanner.py https://example.com

# Save results to file
python scanner.py https://example.com > report.json

# Multiple websites
python scanner.py https://site1.com https://site2.com
```

## 📁 Project Structure

```
bejaa-optimization-scanner/
├── app.py                 # Flask web application
├── scanner.py            # Main scanner logic
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/
│   └── index.html       # Web interface
├── static/
│   ├── css/            # Stylesheets (to be created)
│   └── js/
│       └── scanner.js  # Frontend logic
├── modules/             # Individual scanner modules
└── reports/             # Generated scan reports
```

## 🔧 Configuration

Edit `config.py` to customize:
- Performance thresholds
- Security headers to check
- SEO tags to analyze
- Scoring weights
- Company information

## 🚀 Deployment

### For Production:
1. **Use Gunicorn**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

2. **Set up Nginx** (recommended):
   ```nginx
   server {
       listen 80;
       server_name scanner.bejaadigital.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Add SSL** (Let's Encrypt):
   ```bash
   sudo certbot --nginx -d scanner.bejaadigital.com
   ```

## 📊 Integration with Bejaa Digital

### Marketing Integration:
1. Add scanner link to Bejaa Digital website
2. Create "Free Website Health Check" landing page
3. Set up email automation for scan results
4. Add consultation booking links

### Lead Generation:
1. Capture emails for full PDF reports
2. Follow-up sequence with optimization tips
3. Case studies showing before/after results
4. Special offers for scanner users

## 🎨 Customization

### Branding:
1. Update logo in `static/images/`
2. Modify colors in CSS
3. Update contact information in `config.py`
4. Customize report templates

### Features to Add:
1. Google Lighthouse integration
2. Broken links checker
3. Competitor comparison
4. Historical tracking
5. API for external integration

## 🐛 Troubleshooting

### Common Issues:

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Website not accessible**
   - Check internet connection
   - Verify URL is correct
   - Website might block automated scans

3. **Slow scans**
   - Increase timeouts in `config.py`
   - Use caching for repeated scans
   - Consider async scanning

4. **Memory issues**
   - Limit concurrent scans
   - Clean up old reports
   - Use streaming for large pages

## 📈 Next Steps

### Phase 1 (Week 1-2): MVP
- [x] Basic scanner with 4 categories
- [x] Web interface
- [ ] PDF report generation
- [ ] Email capture form

### Phase 2 (Week 3-4): Advanced Features
- [ ] Google Lighthouse integration
- [ ] Broken links detection
- [ ] Image optimization analysis
- [ ] Competitor comparison

### Phase 3 (Week 5-6): Production Ready
- [ ] User accounts
- [ ] Scheduled scans
- [ ] API for developers
- [ ] Analytics dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is proprietary software of Bejaa Digital.

## 📞 Support

For support, contact:
- Email: hello@bejaadigital.com
- Website: https://bejaadigital.com
- Documentation: [Add documentation link]

---

**Built with ❤️ by Bejaa Digital Team**  
*Helping businesses optimize their online presence since 2024*