#!/usr/bin/env python3
"""Mind Map 34 — The school-age child. Content spec; layout in mindmap_lib."""

SPEC = {
    "aria": "Mind Map 34: the school-age child, roughly six to twelve years",
    "series_line": "ICU AND YOU  \u00b7  MIND MAP SERIES  \u00b7  No. 34",
    "title": "The school-age child \u2014 roughly six to twelve years",
    "closing": "They can finally tell you what is wrong. The difficulty is that they have also "
               "learned to hide it, to be brave, and to say they are fine.",
    "stations": [
        {
            "anchor": "FIRST, THE DIFFERENCE",
            "point": "The age that can talk, and will understate",
            "colour": "sky",
            "branches": [
                {"title": "THE AIRWAY HAS GROWN UP", "bullets": [
                    "Adenotonsillar tissue peaks at two to six and is now regressing",
                    "By about eight the cords, not the cricoid, are the narrowest point",
                    "Cuffed tubes throughout; watch the pressure rather than guess",
                    "Loose teeth and orthodontic hardware are laryngoscopy hazards",
                    "The post-tonsillectomy bleed is theirs, and it is an airway problem",
                ]},
                {"title": "THE CIRCULATION AT LAST BEHAVES", "bullets": [
                    "Output is no longer substantially rate-dependent",
                    "Resistance and blood pressure are climbing towards adult values",
                    "A mean above 65 is agreed from twelve. Below that, still nothing",
                    "They compensate better than a toddler, then fail later and faster",
                ]},
                {"title": "SIZE, DOSE AND FLUID", "bullets": [
                    "Weight estimation is more reliable now, but weigh them if you can",
                    "Maintenance still 4-2-1; resuscitation 10 mL/kg, not the adult litre",
                    "Adult algorithms from puberty. Before that, per kilogram",
                    "Body habitus varies hugely. Age tells you less than it did",
                ]},
                {"title": "THE CHILD IN THE BED IS A PERSON", "bullets": [
                    "Address the child first. They notice which way round you do it",
                    "Concrete thinkers. Say what happens, in order, without metaphor",
                    "The fears have changed: death, disfigurement, loss of control",
                    "Assent matters even when the parent consents. So does privacy",
                ]},
            ],
        },
        {
            "anchor": "WHAT FILLS THE UNIT",
            "point": "Asthma, trauma, and sugar",
            "colour": "moss",
            "branches": [
                {"title": "ASTHMA, WHICH STILL KILLS", "bullets": [
                    "The peak age for admission, and for preventable death",
                    "Salbutamol by spacer unless too sick; ipratropium early",
                    "Then magnesium, then an infusion by local policy",
                    "A quiet chest in a tiring child is the emergency, not the noise",
                    "Ask about previous ICU, previous intubation, recent steroids",
                ]},
                {"title": "MAJOR TRAUMA", "bullets": [
                    "The leading cause of death in this age group in Australia",
                    "Bicycles, pedestrians, motor vehicles, falls, and horses",
                    "Handlebar injury: pancreas, duodenum, abdomen deceptively soft",
                    "Seatbelt sign: bowel, mesentery, Chance fracture until excluded",
                    "A normal blood pressure is not a normal circulation. They crash late",
                ]},
                {"title": "DIABETIC KETOACIDOSIS", "bullets": [
                    "Often the first presentation of type 1 diabetes at this age",
                    "May look like abdominal pain, vomiting, or a chest infection",
                    "Cerebral oedema is rare, catastrophic, and the thing that kills",
                    "Headache, falling conscious state, bradycardia, hypertension",
                    "Follow the unit protocol exactly. Do not improvise the fluids",
                ]},
                {"title": "SEPSIS AND THE UNWELL CHILD", "bullets": [
                    "Meningococcal disease is rarer than it was, and still moves in hours",
                    "Febrile neutropenia in an oncology child is time-critical",
                    "Ask what they are usually like. Parents describe change precisely",
                    "Perfusion, lactate and conscious state before blood pressure",
                ]},
            ],
        },
        {
            "anchor": "THE ONE YOU CANNOT MISS",
            "point": "Myocarditis, wearing a gastroenteritis costume",
            "colour": "rust",
            "branches": [
                {"title": "WHY IT IS MISSED", "bullets": [
                    "Vomiting, lethargy and abdominal pain \u2014 so, as gastroenteritis",
                    "The child looks mottled and tired and is labelled dehydrated",
                    "A fluid bolus makes them worse. That is the diagnostic moment",
                    "Tachycardia out of proportion to the fever and to the story",
                ]},
                {"title": "WHAT SHOULD MAKE YOU LOOK", "bullets": [
                    "Respiratory distress without wheeze or crackles, in a vomiting child",
                    "Hepatomegaly, a gallop, or a raised jugular venous pressure",
                    "Chest film with a big heart; ECG with low voltages or ST change",
                    "Troponin and a bedside echo answer the question quickly",
                ]},
                {"title": "AND THE OTHERS THAT HIDE", "bullets": [
                    "Appendicitis presenting late, because they said they were fine",
                    "Testicular torsion in a boy who will not volunteer where it hurts",
                    "Anaphylaxis called asthma \u2014 ask about food, and look for the rash",
                    "Toxic shock, after a burn, a wound, or nothing you can find",
                ]},
            ],
        },
        {
            "anchor": "NAMED PLAINLY",
            "point": "The mind, and harm",
            "colour": "plum",
            "branches": [
                {"title": "SELF-HARM AND INGESTION", "bullets": [
                    "At the top of this age band, ingestions stop being accidental",
                    "Ask directly and privately. Suspected abuse: ask little, refer early",
                    "Paracetamol is commonest, and forgiving if you catch it",
                    "Every deliberate ingestion needs a mental health assessment",
                ]},
                {"title": "CHILD PROTECTION, DIFFERENT SHAPE", "bullets": [
                    "Physical abuse presents less often; neglect and sexual abuse more",
                    "An injury that does not fit the story still does not fit the story",
                    "The child may protect the adult. Silence is not agreement",
                    "Every NSW clinician is a mandatory reporter. Suspicion is enough",
                ]},
                {"title": "THE THINGS THEY WILL NOT SAY", "bullets": [
                    "Pain, because they are being brave, or because it means a needle",
                    "Fear, because the parent is there and they are protecting them",
                    "What they think is happening \u2014 usually worse than the truth. Ask",
                ]},
            ],
        },
        {
            "anchor": "BEFORE THE TEAM ARRIVES",
            "point": "What to do in the first hour",
            "colour": "slate",
            "branches": [
                {"title": "THE CALL", "bullets": [
                    "NETS 1300 36 2500 in NSW. Ring early, stand down later",
                    "A real weight, written where everybody can see it",
                    "Glucose in every drowsy or fitting child, every time",
                    "Nothing is lost by a phone call and a great deal is lost by waiting",
                ]},
                {"title": "NUMBERS WORTH KNOWING COLD", "bullets": [
                    "Fluid 10 mL/kg. Adrenaline 10 microgram/kg. Defibrillation 4 J/kg",
                    "Glucose 2 mL/kg of ten per cent",
                    "Cuffed tube, age over four plus three and a half",
                    "Check every one of them against your own formulary before use",
                ]},
            ],
        },
        {
            "anchor": "THROUGHOUT",
            "point": "The part that lasts longer than the illness",
            "colour": "gold",
            "branches": [
                {"title": "WHILE THEY ARE HERE", "bullets": [
                    "Explain every procedure to the child, in order, before it happens",
                    "Analgesia planned, not rescued. Let them score it themselves",
                    "Delirium is common, under-recognised, and worth screening for",
                    "Let the parents stay, including during procedures, if they want to",
                ]},
                {"title": "AND AFTERWARDS", "bullets": [
                    "School is their occupation. Ask about return to learning",
                    "Post-traumatic stress is real in this age group and in their parents",
                    "The sibling at home has had a frightening week, unexplained",
                ]},
            ],
        },
    ],
}
