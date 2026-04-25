#!/usr/bin/env python3
"""
outreach_researcher.py — Multi-Dimensional Contact Research Agent

RESEARCH METHODOLOGY (4 Dimensions):
1. CONFERENCES: Speaker lists, session pages, event programs
2. PUBLICATIONS: Articles authored, case studies, white papers
3. AFFILIATIONS: Universities, professional associations, boards
4. MEDIA: Podcasts, webinars, video interviews

RESEARCH FINDING:
LinkedIn robots.txt blocks search-engine indexing of individual profiles.
  → Exact linkedin.com/in/ URLs are NOT discoverable via public web search.
  → LinkedIn search links are the best available proxy.
  → Enrichment via conferences/publications/affiliations provides higher-value context.

[CITE: PostKing2026] PostKing.io A/B test (4,200+ requests). Notes referencing specific content = 48% acceptance. https://postking.io/blog/linkedin-connection-request-templates-sales
  → Referencing a conference talk or article they authored = 3x more effective than generic notes.

SRP: ONLY researches and enriches contact data. No drafting, no tracking.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

# Enrichment database — compiled from multi-dimensional research
ENRICHMENT_DB = {
    "Renzo di Furia": {
        "conferences": [
            {"name": "Smart Buildings Smart Cities 2022", "url": "https://www.aialosangeles.org/home/aiala-events/technology-conference/smart-cities-speaker-bios-2022/", "role": "Speaker — RDF Consulting Services"},
        ],
        "publications": [
            {"title": "Getting Creative with Construction Technology: A Guide to Prototyping", "url": "https://sketchup.trimble.com/blog/en-US/article/getting-creative-with-construction-technology-a-guide-to-prototyping", "publisher": "Trimble/SketchUp"},
            {"title": "Fresh Thinking for Construction", "url": "https://aecmag.com/features/fresh-thinking-for-construction/", "publisher": "AEC Magazine"},
            {"title": "Turner Construction Case Study", "url": "https://www.trimble.com/blog/construction/en-US/article/turner-construction-case-study", "publisher": "Trimble"},
        ],
        "affiliations": [
            {"org": "University of Washington — Applied Research Consortium", "url": "https://research.be.uw.edu/2023/10/11/industry-faculty-student-collaboration-through-the-applied-research-consortium/", "role": "Industry collaborator, course developer"},
            {"org": "Trimble Visiting Professionals Program", "url": "", "role": "Visiting professional"},
            {"org": "Carpenters' International Training Center, Las Vegas", "url": "", "role": "Curriculum developer"},
        ],
        "media": [
            {"title": "Skydio webinar: Turner Construction — Inside the Jobsite of the Future", "url": "https://www.skydio.com/resources/webinars/turner-construction-inside-the-job-site-of-the-future", "type": "webinar"},
        ],
        "projects": [
            {"name": "Sydney Opera House Research Project (2018)", "note": "AGC Build Washington Excellence in Innovation award"},
            {"name": "SeaTac Concourse C Expansion", "note": "UW case study, $399M GC/CM"},
        ],
        "linkedin_discoverable": False,
        "research_note": "Exact linkedin.com/in/ URL blocked by LinkedIn from search indexing. Multiple articles reference 'Follow Renzo on LinkedIn' as text link but URL is not exposed. Search directly on LinkedIn for 'Renzo di Furia'.",
    },
    "Joshua Hostetler": {
        "conferences": [],
        "publications": [
            {"title": "Behind the Build: Director of BIM & Digital Technology at AECOM", "url": "https://www.autodesk.com/blogs/construction/behind-the-build-interview-with-joshua-hostetler-director-of-bim-digital-technology-at-aecom/", "publisher": "Autodesk"},
            {"title": "40 Under 40: Champions of Construction 2024 (#1)", "url": "https://www.autodesk.com/blogs/construction/40-under-40-champions-of-construction-2024/", "publisher": "Autodesk"},
            {"title": "The Power of BIM Partnership", "url": "https://designgroup.us.com/insights/power-bim-partnership-conversation-bim-managers-new-osuwmc-tower-project", "publisher": "DesignGroup"},
        ],
        "affiliations": [
            {"org": "AIA Columbus — Board of Directors (Associate Director, 2021-2023)", "url": "https://aiacolumbus.org/welcome-the-aia-columbus-2023-board-of-directors/", "role": "Associate Director"},
            {"org": "AIA Ohio Directory of Members", "url": "https://aiaohio.org/wp-content/uploads/2025/01/Directory-FINAL.pdf", "role": "Assoc. AIA, AECOM"},
            {"org": "Bowling Green State University", "url": "", "role": "B.S. Architecture, 2008-2012"},
        ],
        "media": [],
        "projects": [
            {"name": "Project Create Tool", "note": "Reduced project setup time by 90-95%, used on 160+ projects"},
            {"name": "OSU Wexner Medical Center Tower", "note": "BIM partnership with DesignGroup and HDR"},
        ],
        "linkedin_discoverable": False,
        "research_note": "Exact linkedin.com/in/ URL not publicly discoverable. Confirmed existence via ZoomInfo/RocketReach but URL behind paywall. Search directly on LinkedIn for 'Joshua Hostetler AECOM'.",
    },
    "Phil Lazarus": {
        "conferences": [
            {"name": "REDAS BIM Symposium 2018", "url": "https://sia.org.sg/redas-bim-symposium-2018/", "role": "Speaker — 'Preparing for IDD from the Consultant View' (Aurecon)"},
            {"name": "BuiltWorlds Construction Tech Conference 2023", "url": "https://builtworlds.com/event/2023-construction-tech-conference/", "role": "Panelist — 'Does BIM Need a Re-Brand?' (Lendlease)"},
            {"name": "Chicago Build Expo 2023", "url": "https://blog.databid.com/blog/the-midwests-largest-construction-design-show-chicago-build-expo-2023", "role": "Confirmed Speaker (Lendlease)"},
            {"name": "SCAL Seminar 2019", "url": "https://channeo.sg/cn/wp-content/uploads/2019/06/20190817-SCAL-Conditions-of-Contract-in-Todays-Built-Environment-1.pdf", "role": "Speaker — 'BIM Contractual Obligations' (Aurecon)"},
        ],
        "publications": [
            {"title": "Singapore BIM Guide V1 — Legal & Contractual Workgroup", "url": "", "publisher": "Building and Construction Authority Singapore"},
            {"title": "Aurecon Asia Digital Engineering COE Launch", "url": "https://asiamanufacturingnewstoday.com/2018/05/aurecon-strengthens-presence-asia-centre-excellence-digital-engineering/", "publisher": "Asia Manufacturing News Today"},
        ],
        "affiliations": [
            {"org": "Singapore BIM Guide Workgroup", "url": "", "role": "Resource Person — Senior BIM Specialist, Arup"},
            {"org": "University of Southern California", "url": "", "role": "Bachelor of Architecture"},
            {"org": "University of Missouri-Kansas City", "url": "", "role": "MBA, Entrepreneurship focus"},
        ],
        "media": [],
        "projects": [
            {"name": "Marina Bay Sands", "note": "BIM Leader, Aedas Singapore (2006-2007)"},
            {"name": "O'Hare International Airport", "note": "Digital Delivery Leader, Connect Chicago Alliance"},
        ],
        "linkedin_discoverable": False,
        "research_note": "Exact linkedin.com/in/ URL not publicly discoverable. Profile may be private or use non-standard vanity URL. Extensive professional presence via TheOrg, AdvisoryExcellence, conference speaker pages. Search directly on LinkedIn for 'Phil Lazarus Lendlease'.",
    },
    "Gary Chapman": {
        "conferences": [
            {"name": "Skydio webinar — Inside the Jobsite of the Future", "url": "https://www.skydio.com/resources/webinars/turner-construction-inside-the-job-site-of-the-future", "role": "Featured speaker — Regional VDC Manager"},
            {"name": "DroneDeploy DDC '23 Conference", "url": "https://www.dronedeploy.com/resources/collections/ddc2023/changing-the-game-turners-unique-approach-to-an-organizational-reality-capture-program", "role": "Speaker with Cole Milberger"},
        ],
        "publications": [
            {"title": "Marquis Who's Who — Success in Construction Sector", "url": "https://www.24-7pressrelease.com/press-release/510741/marquis-whos-who-selects-gary-chapman-for-success-in-the-construction-sector", "publisher": "24-7 Press Release"},
        ],
        "affiliations": [
            {"org": "Associated Builders & Contractors of Greater Tennessee", "url": "", "role": "Board/committee member — drone, AI, robotics"},
            {"org": "Western Carolina University", "url": "", "role": "Bachelor's degree, 2003-2005"},
            {"org": "Penn Foster Group", "url": "", "role": "Certification, 2008-2010"},
        ],
        "media": [
            {"title": "Built Different Podcast S03 E04", "url": "https://creators.spotify.com/pod/profile/builtdifferentpod/episodes/Episode-46---AI--safety-and-the-real-story-behind-construction-tech-e35mn7p", "type": "podcast"},
            {"title": "Built Different Podcast — Season 3 Reunion", "url": "https://creators.spotify.com/pod/profile/builtdifferentpod", "type": "podcast"},
        ],
        "projects": [
            {"name": "Turner Construction — Organizational Reality Capture Program", "note": "DroneDeploy Innovator of the Year 2022"},
        ],
        "linkedin_discoverable": False,
        "research_note": "Exact linkedin.com/in/ URL not publicly discoverable. Site:linkedin.com/in/ search returned zero results. Profile confirmed via RocketReach, Crunchbase, Datanyze. Search directly on LinkedIn for 'Gary Chapman Turner Construction Nashville'.",
    },
    "Sagar S Gandhi": {
        "conferences": [
            {"name": "Construction Technology Day 2023 — IIT Bombay", "url": "https://ctai.in/construction-technology-day-2023/", "role": "Speaker & Panelist — Head of Strategy & Business Excellence, SP E&C"},
            {"name": "GeoSmart Infrastructure 2023", "url": "https://geospatialworld.net/gsinfra/2023/speakers.php", "role": "Speaker — Head of Strategy and Business Excellence"},
            {"name": "Autodesk University 2024", "url": "https://www.autodesk.com/autodesk-university/class/Breaking-Ground-Indias-Oldest-Construction-Company-Adopts-ACC-to-Close-the-Gap-Between-the-Field-and-the-Office-2024", "role": "Session participant — Shapoorji Pallonji ACC adoption"},
            {"name": "Tekla User Days 2019 India, Chennai", "url": "https://www.epcworld.in/trimble-hosts-tekla-user-days-2019-india-in-chennai/", "role": "Speaker — AGM Operations & Technology"},
        ],
        "publications": [
            {"title": "Customizing the Last Planner System Components", "url": "https://link.springer.com/chapter/10.1007/978-981-99-5455-1_9", "publisher": "Springer — Sustainable Lean Construction (ILCC 2022)"},
            {"title": "A Digital Revolution in Indian Construction", "url": "https://www.autodesk.com/blogs/construction/a-digital-revolution-in-indian-construction/", "publisher": "Autodesk Construction Blog"},
            {"title": "Navigating the Digital Transformation in India's Construction Industry", "url": "https://www.autodesk.com/blogs/construction/navigating-the-digital-transformation-in-indias-construction-industry/", "publisher": "Autodesk Construction Blog"},
            {"title": "Autodesk Plan-to-Pay Customer Story", "url": "https://www.autodesk.com/in/customer-stories/sp-plan-to-pay", "publisher": "Autodesk India"},
        ],
        "affiliations": [
            {"org": "ILCE — Indian Institute for Lean Construction Excellence", "url": "https://www.ilce.in/ilcemembers/mr-sagar-gandhi/", "role": "Board of Directors (since 2015), Chartered Member"},
            {"org": "CTAI Foundation — Construction Technology Alliance Institute", "url": "https://ctai.in/", "role": "Core Team Member"},
            {"org": "Stanford University", "url": "", "role": "M.S. Construction Engineering & Management"},
            {"org": "Maharashtra Institute of Technology, Pune University", "url": "", "role": "B.E. Civil Engineering"},
        ],
        "media": [],
        "projects": [
            {"name": "Shapoorji Pallonji ACC Digital Transformation", "note": "5D VDC case study — connected workflows, ACC adoption"},
        ],
        "linkedin_discoverable": False,
        "research_note": "Exact linkedin.com/in/ URL not publicly discoverable. Strong industry-visible presence (conference keynotes, Springer publication, Autodesk case studies, ILCE board). Search directly on LinkedIn for 'Sagar Gandhi Shapoorji Pallonji'.",
    },
}


def enrich_contact(contact_name: str) -> dict:
    """Return enriched research data for a contact."""
    return ENRICHMENT_DB.get(contact_name, {
        "linkedin_discoverable": False,
        "research_note": "No enrichment data available. Recommend direct LinkedIn search.",
        "conferences": [],
        "publications": [],
        "affiliations": [],
        "media": [],
        "projects": [],
    })


def batch_enrich(contact_names: list) -> dict:
    """Enrich multiple contacts and return report."""
    results = {}
    for name in contact_names:
        results[name] = enrich_contact(name)
    return results


def generate_enrichment_report() -> dict:
    """Generate summary report of all enrichment data."""
    total = len(ENRICHMENT_DB)
    with_conferences = sum(1 for v in ENRICHMENT_DB.values() if v.get("conferences"))
    with_publications = sum(1 for v in ENRICHMENT_DB.values() if v.get("publications"))
    with_affiliations = sum(1 for v in ENRICHMENT_DB.values() if v.get("affiliations"))
    with_media = sum(1 for v in ENRICHMENT_DB.values() if v.get("media"))
    linkedin_found = sum(1 for v in ENRICHMENT_DB.values() if v.get("linkedin_discoverable"))

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_contacts_researched": total,
        "with_conferences": with_conferences,
        "with_publications": with_publications,
        "with_affiliations": with_affiliations,
        "with_media": with_media,
        "linkedin_direct_urls_found": linkedin_found,
        "linkedin_direct_urls_total": total,
        "methodology_note": "LinkedIn blocks search-engine indexing of individual profiles. Direct linkedin.com/in/ URLs are NOT discoverable via public web search. Enrichment focuses on conferences, publications, affiliations, and media where URLs ARE publicly available.",
        "research_citations": [
            "LinkedIn robots.txt blocks search-engine indexing of individual profiles",
            "PostKing2026 — PostKing.io A/B test: notes referencing specific content = 48% acceptance (3x generic). https://postking.io/blog/linkedin-connection-request-templates-sales",
        ],
    }


if __name__ == "__main__":
    report = generate_enrichment_report()
    print(json.dumps(report, indent=2))
