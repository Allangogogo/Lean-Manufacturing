"""
Lean 2.0 Checklist Migration
- Add checklist_items table (template: per-dimension checklist with L1-L5 descriptions)
- Add checklist_responses table (user responses for each assessment)
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'leanops.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Checklist items template (static reference data)
    c.execute("""
        CREATE TABLE IF NOT EXISTS lean20_checklist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dimension_code VARCHAR(1) NOT NULL,
            item_code VARCHAR(10) NOT NULL,
            item_name TEXT NOT NULL,
            item_weight NUMERIC(3,2) NOT NULL DEFAULT 0.15,
            l1_desc TEXT NOT NULL DEFAULT '',
            l2_desc TEXT NOT NULL DEFAULT '',
            l3_desc TEXT NOT NULL DEFAULT '',
            l4_desc TEXT NOT NULL DEFAULT '',
            l5_desc TEXT NOT NULL DEFAULT '',
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(dimension_code, item_code)
        )
    """)

    # 2. Checklist responses (per assessment)
    c.execute("""
        CREATE TABLE IF NOT EXISTS lean20_checklist_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            score INTEGER NOT NULL DEFAULT 1 CHECK(score BETWEEN 1 AND 5),
            evidence TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES lean20_assessments(id),
            FOREIGN KEY (item_id) REFERENCES lean20_checklist_items(id),
            UNIQUE(assessment_id, item_id)
        )
    """)

    # 3. Seed checklist items for each dimension
    # Operations (O) - 7 items
    o_items = [
        ('O01', '5S & Visual Management', 0.18,
         'No 5S; workplace disorganized; items cannot be found',
         '5S started but hard to sustain; basic visual boards exist',
         '5S maintained well; visual mgmt comprehensive; Gemba board active',
         '5S is culture; visual mgmt drives decisions; autonomous audit',
         '5S self-sustaining; visual innovation; industry benchmark'),
        ('O02', 'Standard Work', 0.18,
         'No standard work docs; methods vary by operator',
         'Some SOPs exist but outdated; execution inconsistent',
         'SOPs complete & current; execution consistent; regular review cycle',
         'SOPs continuously improved; operator-driven updates; best-practice sharing',
         'Standard work as innovation platform; self-evolving; industry reference'),
        ('O03', 'TPM & Equipment', 0.16,
         'Breakdown maintenance only; no PM plan; OEE <55%',
         'Basic PM started; OEE 55-65%; AM awareness emerging',
         'TPM system running; OEE 70-80%; AM participation >60%',
         'Predictive maintenance; OEE 80-85%; AM >80%; zero breakdown target',
         'Autonomous maintenance culture; OEE >90%; world-class reliability'),
        ('O04', 'Quality System', 0.16,
         'End-of-line inspection only; no process control; high defect rate',
         'SPC started at key stations; basic quality tools; COPQ tracked',
         'SPC widespread; process control dominant; 8D/A3 for problem solving',
         'Zero-defect culture; Six Sigma projects active; quality cost <2%',
         'Six Sigma level (3.4PPM); quality as competitive advantage'),
        ('O05', 'Flow & Pull', 0.14,
         'Push production; high WIP; long lead times; no pull signals',
         'Kanban piloted in some lines; WIP reduction started',
         'Pull system running in key value streams; WIP controlled; lead time reduced 30%+',
         'End-to-end pull; Heijunka leveling; JIT delivery to key customers',
         'Fully synchronized value stream; demand-driven; zero-waste flow'),
        ('O06', 'Problem Solving', 0.10,
         'Firefighting; no structured approach; problems recur',
         'Basic 5-Why; some A3 usage; root cause analysis occasional',
         'A3/8D standard practice; PDCA cycle embedded; countermeasures verified',
         'Data-driven problem solving; predictive analytics; cross-functional Kaizen',
         'Self-healing systems; AI-assisted root cause; organizational learning loop'),
        ('O07', 'Supply Chain Integration', 0.08,
         'No supplier collaboration; adversarial relationships; high inventory',
         'Basic supplier evaluation; safety stock for key items; some communication',
         'Supplier scorecard active; VMI pilots; joint improvement projects',
         'Supplier lean coaching; JIT supply; risk-sharing partnerships',
         'Extended lean enterprise; ecosystem optimization; value network design'),
    ]

    # Digital (D) - 6 items
    d_items = [
        ('D01', 'Data Collection', 0.20,
         'Paper records only; manual data entry; no real-time data',
         'MES/ERP deployed; key equipment connected; electronic records',
         'IoT data collection; real-time dashboards; automated reporting',
         'AI-driven data quality; predictive analytics; digital twin pilot',
         'Autonomous data ecosystem; self-validating; AI-curated insights'),
        ('D02', 'Process Visibility', 0.18,
         'No production visibility; status unknown until end-of-line',
         'Electronic Kanban; production status boards; basic tracking',
         'Real-time OEE monitoring; SPC auto-alerts; Andon system',
         'Digital twin for key processes; what-if simulation; AI anomaly detection',
         'Full digital twin; real-time optimization; autonomous scheduling'),
        ('D03', 'Quality Digitization', 0.18,
         'Manual inspection only; no digital quality data; paper records',
         'Digital inspection records; SPC software; basic traceability',
         'Automated inspection data; SPC auto-monitoring; full traceability',
         'AI visual inspection (<100ms); predictive quality; ML defect classification',
         'Zero-defect AI system; self-adjusting process parameters; digital quality passport'),
        ('D04', 'Maintenance Digitization', 0.16,
         'Paper maintenance logs; breakdown-only; no data analysis',
         'CMMS deployed; PM scheduled; MTBF/MTTR tracked digitally',
         'Condition monitoring (vibration/temp); predictive models; digital work orders',
         'AI predictive maintenance; remaining useful life prediction; digital twin for assets',
         'Self-healing equipment; AI autonomous maintenance scheduling; prescriptive maintenance'),
        ('D05', 'Decision Support', 0.16,
         'Decisions based on experience; no data-driven culture',
         'BI dashboards for management; basic KPI reporting; manual analysis',
         'Automated KPI dashboards; drill-down analytics; data-driven meetings',
         'AI decision support; scenario simulation; prescriptive recommendations',
         'Autonomous decision systems; AI-driven optimization; human-AI collaborative decisions'),
        ('D06', 'Digital Culture', 0.12,
         'Digital resistance; low IT literacy; paper preference',
         'Basic digital training; some digital champions; mixed adoption',
         'Digital literacy programs; data-driven mindset; digital Kaizen events',
         'Digital innovation culture; citizen developers; AI-augmented workforce',
         'Digital-native organization; continuous digital evolution; industry digital leader'),
    ]

    # Green (G) - 6 items
    g_items = [
        ('G01', 'Energy Management', 0.20,
         'No energy tracking; only pay bills; no efficiency awareness',
         'Energy metering started; major equipment monitored; basic targets',
         'Process-level energy monitoring; ISO 50001 foundation; energy Kaizen',
         'Energy management system (ISO 50001); real-time optimization; green electricity >30%',
         'Carbon-neutral energy; 100% renewable; energy-positive operations'),
        ('G02', 'Carbon Footprint', 0.20,
         'No carbon data; no emission awareness; no tracking',
         'Scope 1+2 emissions calculated; basic carbon inventory; annual report',
         'Product carbon footprint (cradle-to-gate); hot-spot identification; reduction targets',
         'CBAM-compliant carbon accounting; carbon labels on products; Scope 3 tracking',
         'Carbon-negative potential; carbon data as service; industry carbon benchmark'),
        ('G03', 'Waste & Circularity', 0.18,
         'High waste; no recycling; scrap as cost of doing business',
         'Basic waste segregation; recycling for valuable scrap; waste reduction targets',
         'Waste reduction Kaizen; circular economy pilots; scrap rate <3%',
         'Closed-loop material flows; industrial symbiosis; scrap <1%',
         'Zero-waste manufacturing; full circularity; waste-to-value innovation'),
        ('G04', 'Environmental Compliance', 0.18,
         'Non-compliance issues; no environmental management system',
         'Basic compliance (emissions/wastewater); environmental KPIs tracked',
         'ISO 14001 certified; proactive environmental management; beyond compliance',
         'Integrated ESG reporting; environmental excellence; green supply chain requirements',
         'Environmental leadership; regenerative operations; industry sustainability benchmark'),
        ('G05', 'Green Product Design', 0.14,
         'No environmental consideration in product design',
         'Basic DfE awareness; material substitution considerations',
         'LCA for key products; eco-design guidelines; green material selection',
         'Full product LCA; eco-innovation pipeline; green product portfolio',
         'Cradle-to-cradle design; green product differentiation; sustainability as brand'),
        ('G06', 'Green Supply Chain', 0.10,
         'No supplier environmental requirements; no green procurement',
         'Basic supplier environmental screening; green procurement policy drafted',
         'Supplier carbon data collection; green procurement active; logistics optimization',
         'Scope 3 reduction programs; supplier carbon coaching; green logistics',
         'Carbon-neutral supply chain; ecosystem-level sustainability; green value network'),
    ]

    # Resilience (R) - 6 items
    r_items = [
        ('R01', 'Supply Risk Management', 0.20,
         'Single-source for key materials; no risk assessment; reactive to disruptions',
         'Risk register started; safety stock for top-10 items; basic contingency',
         'Dual-source >80%; supplier risk scoring; scenario planning; 7-day buffer',
         'AI supply risk monitoring; dynamic buffering; stress-test program; dual-source 100%',
         'Self-healing supply network; AI-adaptive sourcing; resilience as competitive advantage'),
        ('R02', 'Operational Continuity', 0.18,
         'No BCP; single-point-of-failures common; long recovery time',
         'Basic BCP drafted; key process redundancy planned; emergency response SOP',
         'BCP tested & updated; alternative production plans; recovery <48h',
         'Digital twin for continuity planning; auto-failover; recovery <8h',
         'Self-reconfiguring operations; zero-disruption target; continuous resilience testing'),
        ('R03', 'Demand Flexibility', 0.18,
         'Rigid production; long changeover; cannot absorb demand swings',
         'SMED started; flexibility improvement; some demand buffering',
         'Quick changeover (<15min); flexible capacity; demand sensing',
         'AI-driven demand forecasting; flexible automation; dynamic capacity allocation',
         'Autonomous demand-response; reconfigurable manufacturing; mass customization'),
        ('R04', 'Cyber & Data Resilience', 0.16,
         'No cybersecurity measures; no data backup strategy; high vulnerability',
         'Basic firewall & antivirus; regular backups; IT security policy',
         'IEC 62443 compliance; OT/IT segmentation; incident response team; tested backups',
         'Zero-trust architecture; AI threat detection; cyber resilience testing; <1h recovery',
         'Self-healing IT/OT; quantum-ready security; cyber resilience benchmark'),
        ('R05', 'Organizational Resilience', 0.16,
         'Rigid hierarchy; slow decision-making; crisis paralysis',
         'Crisis communication plan; cross-functional response team; basic delegation',
         'Rapid decision protocols; decentralized authority; learning from disruptions',
         'Anticipatory organization; scenario-based leadership; resilience culture embedded',
         'Adaptive organization; thrives on disruption; antifragile operations'),
        ('R06', 'Financial Resilience', 0.12,
         'Thin margins; no reserves; one disruption away from crisis',
         'Cash reserve policy; basic financial risk management; insurance coverage',
         'Diversified revenue; stress-tested financials; hedging strategies',
         'Dynamic financial modeling; real-time risk-adjusted pricing; AI treasury management',
         'Financially antifragile; disruption creates opportunity; strategic reserves'),
    ]

    # Human-Centric (H) - 6 items
    h_items = [
        ('H01', 'Employee Participation', 0.20,
         'Top-down only; employees follow orders; no suggestion system',
         'Suggestion box exists; <10% participation; basic team meetings',
         'Kaizen suggestion system; 30-50% participation rate; team-based improvement',
         'Employee-led Kaizen; >70% participation; autonomous improvement teams',
         'Self-organizing improvement; 90%+ participation; innovation from everyone'),
        ('H02', 'Skill Development', 0.20,
         'Single-skill operators; no training plan; skill gaps unaddressed',
         'Basic training plan; multi-skill training started; <30% multi-skilled',
         'Skill matrix active; multi-skill >50%; structured training with assessment',
         'T-shaped talent program; multi-skill >70%; data literacy; AI upskilling',
         'Continuous learning organization; self-directed development; skill innovation lab'),
        ('H03', 'Workplace Wellbeing', 0.18,
         'Ergonomics ignored; safety compliance only; high turnover/stress',
         'Basic ergonomics assessment; safety programs; employee satisfaction survey',
         'Ergonomic improvements active; wellness programs; psychological safety initiatives',
         'Human-centric workplace design; AI-augmented ergonomics; proactive wellbeing',
         'Workplace as talent magnet; optimal human performance; wellbeing as culture'),
        ('H04', 'Empowerment & Autonomy', 0.18,
         'All decisions from management; no frontline authority; strict hierarchy',
         'Some delegation to supervisors; basic decision authority at team lead level',
         'Team-based decision making; Andon pull authority; self-managed work cells',
         'Employee autonomy in process improvement; AI-human decision partnership',
         'Self-governing teams; human-AI symbiosis; distributed decision authority'),
        ('H05', 'Innovation Culture', 0.14,
         'No innovation; management dictates all changes; fear of failure',
         'Innovation suggestion program; occasional improvement workshops',
         'Structured innovation process; Kaizen events; cross-functional innovation teams',
         'Innovation labs; rapid prototyping; employee-driven digital innovation',
         'Continuous innovation engine; breakthrough thinking norm; innovation ecosystem'),
        ('H06', 'Meaningful Work', 0.10,
         'Work as pure task execution; no connection to purpose',
         'Basic communication of company mission; some job enrichment',
         'Clear line-of-sight to customer value; job rotation; skill variety',
         'Purpose-driven work; autonomy+mastery+purpose; human potential development',
         'Work as self-actualization; human flourishing; industry employer-of-choice'),
    ]

    all_items = [
        ('O', o_items),
        ('D', d_items),
        ('G', g_items),
        ('R', r_items),
        ('H', h_items),
    ]

    for dim_code, items in all_items:
        for i, (item_code, item_name, weight, l1, l2, l3, l4, l5) in enumerate(items):
            c.execute("""
                INSERT OR REPLACE INTO lean20_checklist_items
                (dimension_code, item_code, item_name, item_weight, l1_desc, l2_desc, l3_desc, l4_desc, l5_desc, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (dim_code, item_code, item_name, weight, l1, l2, l3, l4, l5, i + 1))

    conn.commit()
    print(f"Seeded {sum(len(items) for _, items in all_items)} checklist items")

    # Verify
    for dim_code in ['O', 'D', 'G', 'R', 'H']:
        count = c.execute("SELECT COUNT(*) FROM lean20_checklist_items WHERE dimension_code=?", (dim_code,)).fetchone()[0]
        print(f"  {dim_code}: {count} items")

    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
