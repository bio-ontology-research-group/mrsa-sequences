import jinja2

templateLoader = jinja2.FileSystemLoader(searchpath="./analyzer")
templateEnv = jinja2.Environment(loader=templateLoader)

def generate_report(data):
    template = templateEnv.get_template('report.html')
    report = template.render(data)
    with open('result.html', 'w') as f:
        f.write(report)
    
