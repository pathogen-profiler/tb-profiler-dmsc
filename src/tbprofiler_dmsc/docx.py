import os
from tbprofiler.models import ProfileResult
from collections import defaultdict

__docx_template_name__ = "dmsc"
__docx_template_file__ = "DR-TB_report_template_V3.docx"


def sanitize(d):
    d = d.replace("-","_")
    return d

def create_variable(profile: ProfileResult, conf: dict) -> dict:
    """Create variables for customised Word document for a TB-Profiler result"""


    data = profile.model_dump()
    drug_variants = defaultdict(list)
    confidence = defaultdict(list)
    for var in data['dr_variants']:
        for d in var['drugs']:
            if d['type']=='drug_resistance':
                if "confidence" not in d: continue
                drug_variants[d['drug']].append(f"{var['gene_name']}_{var['change']}")
                confidence[d['drug']].append(d['confidence'])

    
    # time = datetime.datetime.strptime(data['timestamp'], "%d-%m-%Y %H:%M:%S")

    variables = {
        'id': profile.id,
        'date':data['timestamp'].strftime("%d %b %Y"),
        'sublineage': data['sub_lineage'],
        'pct_reads_mapped': profile.qc.get_percent_reads_mapped(),
        'genome_median_depth': profile.qc.get_target_median_depth(),
        'tbprofiler_version': profile.pipeline.software_version,
        'resistant_drugs': ", ".join([d.capitalize() for d in conf['drugs'] if d in drug_variants]),
        'version': data['pipeline']['software_version'],
        'sensitive': True if data['drtype'] == "Sensitive" else False,
        'mdr': True if data['drtype'] in ("MDR-TB",) else False,
        'pre_xdr': True if data['drtype'] in ("Pre-XDR-TB") else False,
        'xdr': True if data['drtype'] in "XDR-TB" else False,
        'resistant': True if data['drtype'] in ("Other","RR-TB","HR-TB") else False,
        'drtype': data['drtype'],
        'd': profile.model_dump()
    }

    for d in conf['drugs']:
        variables[sanitize(d)+"_variants"] = ", ".join(drug_variants[d]) if len(drug_variants[d])>0 else "Not found"
        variables[sanitize(d)+"_confidence"] = ", ".join(confidence[d]) if len(drug_variants[d])>0 else "-"
        variables[sanitize(d)+"_interpretation"] = "Resistance" if len(drug_variants[d])>0 else "-"



  

    return variables

def get_template():
    """Return the path to the customised Word document template"""
    # return current path + template name
    return os.path.join(os.path.dirname(__file__), "templates", f"{__docx_template_file__}")
    