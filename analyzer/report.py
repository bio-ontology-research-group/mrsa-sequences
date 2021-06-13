import jinja2

# templateLoader = jinja2.FileSystemLoader(searchpath="./analyzer")
templateLoader = jinja2.PackageLoader(__name__, '')
templateEnv = jinja2.Environment(loader=templateLoader)

def generate_report(data):
    template = templateEnv.get_template('report.html')
    report = template.render(data)
    with open('result.html', 'w') as f:
        f.write(report)

    with open('data/result_csvs/identification.csv', 'w') as f:
        for sample_id, data in data['kraken']:
            f.write(sample_id)
            for p, _, name in data:
                f.write(f',{name},{p}')
            f.write('\n')
    
