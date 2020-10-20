from jinja2 import Template

def generate_report(data):
    template = Template('report.html')
    report = template.render(data)
    with open('result.html', 'w') as f:
        f.write(report)
    
