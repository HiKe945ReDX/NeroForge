from jinja2 import Template
from typing import Dict, Any
from src.models import Portfolio

class TemplateGenerator:
    """Generate portfolio HTML from templates"""
    
    def __init__(self):
        self.templates = {
            "modern": self._get_modern_template(),
            "minimal": self._get_minimal_template()
        }
    
    def generate_html(self, portfolio: Portfolio) -> str:
        """Generate HTML portfolio"""
        template = self.templates.get(portfolio.template_id, self.templates["modern"])
        return template.render(
            portfolio=portfolio,
            profile=portfolio.profile,
            projects=portfolio.projects,
            colors=portfolio.theme_colors
        )
    
    def _get_modern_template(self) -> Template:
        """Modern portfolio template"""
        template_str = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ profile.name }} - {{ profile.title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6; 
            color: #333;
            background: linear-gradient(135deg, {{ colors.primary }}15 0%, {{ colors.accent }}10 100%);
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .header { 
            text-align: center; 
            margin-bottom: 4rem; 
            padding: 3rem 0;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .name { 
            font-size: 3rem; 
            font-weight: 700; 
            color: {{ colors.primary }};
            margin-bottom: 0.5rem;
        }
        .title { 
            font-size: 1.5rem; 
            color: {{ colors.secondary }}; 
            margin-bottom: 1rem;
        }
        .bio { 
            font-size: 1.1rem; 
            max-width: 600px; 
            margin: 0 auto;
            color: #666;
        }
        .contact { 
            margin-top: 2rem; 
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
        }
        .contact a { 
            color: {{ colors.primary }};
            text-decoration: none;
            padding: 0.5rem 1rem;
            border: 2px solid {{ colors.primary }};
            border-radius: 25px;
            transition: all 0.3s;
        }
        .contact a:hover { 
            background: {{ colors.primary }};
            color: white;
        }
        .section { 
            margin-bottom: 3rem;
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }
        .section h2 { 
            font-size: 2rem; 
            margin-bottom: 2rem;
            color: {{ colors.primary }};
            border-bottom: 3px solid {{ colors.accent }};
            padding-bottom: 0.5rem;
        }
        .projects-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
            gap: 2rem; 
        }
        .project-card { 
            border: 2px solid #eee;
            border-radius: 12px; 
            padding: 2rem;
            transition: all 0.3s;
            background: #fafafa;
        }
        .project-card:hover { 
            transform: translateY(-5px);
            border-color: {{ colors.accent }};
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }
        .project-title { 
            font-size: 1.3rem; 
            font-weight: 600; 
            margin-bottom: 1rem;
            color: {{ colors.secondary }};
        }
        .project-description { 
            margin-bottom: 1rem;
            color: #666;
        }
        .tech-stack { 
            display: flex; 
            flex-wrap: wrap; 
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        .tech-tag { 
            background: {{ colors.primary }}20;
            color: {{ colors.primary }};
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        .project-links { 
            display: flex; 
            gap: 1rem; 
        }
        .project-links a { 
            color: {{ colors.accent }};
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }
        .project-links a:hover { 
            color: {{ colors.primary }};
        }
        .skills-list { 
            display: flex; 
            flex-wrap: wrap; 
            gap: 1rem; 
        }
        .skill-tag { 
            background: {{ colors.accent }}20;
            color: {{ colors.secondary }};
            padding: 0.6rem 1.2rem;
            border-radius: 20px;
            font-weight: 500;
        }
        .footer {
            text-align: center;
            margin-top: 4rem;
            padding: 2rem;
            color: #666;
        }
        @media (max-width: 768px) {
            .container { padding: 1rem; }
            .name { font-size: 2rem; }
            .projects-grid { grid-template-columns: 1fr; }
            .contact { flex-direction: column; align-items: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1 class="name">{{ profile.name }}</h1>
            <h2 class="title">{{ profile.title }}</h2>
            <p class="bio">{{ profile.bio }}</p>
            <div class="contact">
                {% if profile.email %}
                <a href="mailto:{{ profile.email }}">Email</a>
                {% endif %}
                {% if profile.github_username %}
                <a href="https://github.com/{{ profile.github_username }}" target="_blank">GitHub</a>
                {% endif %}
                {% if profile.linkedin_url %}
                <a href="{{ profile.linkedin_url }}" target="_blank">LinkedIn</a>
                {% endif %}
            </div>
        </header>

        {% if projects %}
        <section class="section">
            <h2>Featured Projects</h2>
            <div class="projects-grid">
                {% for project in projects %}
                <div class="project-card">
                    <h3 class="project-title">{{ project.title }}</h3>
                    <p class="project-description">{{ project.description }}</p>
                    {% if project.tech_stack %}
                    <div class="tech-stack">
                        {% for tech in project.tech_stack %}
                        <span class="tech-tag">{{ tech }}</span>
                        {% endfor %}
                    </div>
                    {% endif %}
                    <div class="project-links">
                        {% if project.github_url %}
                        <a href="{{ project.github_url }}" target="_blank">View Code</a>
                        {% endif %}
                        {% if project.live_url %}
                        <a href="{{ project.live_url }}" target="_blank">Live Demo</a>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
        {% endif %}

        {% if profile.skills %}
        <section class="section">
            <h2>Skills & Technologies</h2>
            <div class="skills-list">
                {% for skill in profile.skills %}
                <span class="skill-tag">{{ skill }}</span>
                {% endfor %}
            </div>
        </section>
        {% endif %}
        
        <footer class="footer">
            <p>Generated by Guidora Portfolio Builder • {{ portfolio.created_at.strftime('%Y') }}</p>
        </footer>
    </div>
</body>
</html>
        '''
        return Template(template_str)
    
    def _get_minimal_template(self) -> Template:
        """Minimal portfolio template"""
        return self._get_modern_template()  # Use modern for now
