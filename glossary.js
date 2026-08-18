/* ICU AND YOU — glossary cards.
   Any <a class="gl" href="glossary.html#id"> becomes click-to-open.
   Without this script the link still works, going to the glossary page. */
(function(){
  var G = {"isbar": {"t": "ISBAR", "x": "Identification, Situation, Background, Assessment, Recommendation", "d": "A structure for handing over or escalating a patient. Its point is that the listener gets your concern in the first sentence rather than the last."}, "peep": {"t": "PEEP", "x": "positive end-expiratory pressure", "d": "Pressure held in the airway at the end of expiration to stop alveoli collapsing. It is what keeps the lung open between breaths."}, "frc": {"t": "FRC", "x": "functional residual capacity", "d": "The volume of air left in the lungs after a normal breath out — the oxygen reservoir you draw on between breaths. Infants have proportionally less of it, which is why they desaturate so fast."}, "brue": {"t": "BRUE", "x": "brief resolved unexplained event", "d": "An episode in an infant under one of altered breathing, colour, tone or responsiveness, which has fully resolved by the time you see them. The risk lies in what might be missed, not in the event itself."}, "sudi": {"t": "SUDI", "x": "sudden unexpected death in infancy", "d": "The sudden death of an infant that was not anticipated. It remains the leading cause of death between one month and one year, and the coroner is involved in every case."}, "intraosseous": {"t": "Intraosseous", "x": null, "d": "Vascular access drilled directly into the marrow cavity of a bone, usually the proximal tibia. Anything that can be given intravenously can be given this way, and it takes under a minute."}, "recession": {"t": "Recession", "x": null, "d": "The indrawing of soft tissue between and below the ribs on inspiration — subcostal, intercostal or sternal. It means the child is generating large negative pressures to move air."}, "grunting": {"t": "Grunting", "x": null, "d": "An expiratory noise made by breathing out against a partly closed glottis. The infant is generating their own PEEP, and it is a late and serious sign."}, "septic-screen": {"t": "Septic screen", "x": null, "d": "The set of cultures and samples taken before antibiotics when infection is suspected — typically blood, urine and, in an infant, cerebrospinal fluid."}, "mandatory-reporter": {"t": "Mandatory reporter", "x": null, "d": "A person legally obliged to report a reasonable suspicion of child abuse or neglect. All clinicians in New South Wales are mandatory reporters. Suspicion is the threshold, not proof."}, "preductal": {"t": "Preductal", "x": null, "d": "Measured upstream of the ductus arteriosus — in practice, the right hand. It reflects the blood reaching the brain, which is why the saturation probe goes there in a newborn."}, "pat": {"t": "Paediatric assessment triangle", "x": null, "d": "Appearance, work of breathing and circulation to skin, judged from the end of the cot before you touch the child. It grades a sick infant in seconds and survives handling, which measurements do not."}, "capillary-refill": {"t": "Capillary refill time", "x": null, "d": "The seconds taken for colour to return after pressing the skin for five seconds. Over two seconds suggests poor perfusion, and in a child it moves before the blood pressure does."}, "nets": {"t": "NETS", "x": "Newborn and paediatric Emergency Transport Service", "d": "The New South Wales retrieval service for newborns and children, reachable on 1300 36 2500. They expect to be called early and uncertain rather than late and sure."}, "cruising": {"t": "Cruising", "x": null, "d": "Walking while holding onto furniture, usually from around ten to twelve months. It matters because a bruise in a baby not yet cruising has almost certainly been inflicted."}, "421": {"t": "4-2-1 rule", "x": null, "d": "Maintenance fluid: 4 mL/kg/h for the first 10 kg, then 2 mL/kg/h for the next 10, then 1 mL/kg/h beyond that. Resuscitation boluses in children are 10 mL/kg, which is a different calculation."}, "hie": {"t": "HIE", "x": "hypoxic-ischaemic encephalopathy", "d": "Brain injury from a period of inadequate oxygen or blood flow around the time of birth. Therapeutic cooling must begin within six hours, which is why the decision is made clinically."}, "ice": {"t": "ICE", "x": "Integrated Clinical Examination", "d": "A clinical examination assessing history, examination and reasoning together rather than as separate skills — a common format in the clinical years of an Australian medical program."}};

  var css = document.createElement("style");
  css.textContent =
    "a.gl{color:inherit;text-decoration:none;border-bottom:1.5px dotted currentColor;" +
      "cursor:help;padding-bottom:.5px}" +
    "a.gl:hover{border-bottom-style:solid}" +
    "a.gl.open{background:rgba(0,0,0,.045)}" +
    ".gl-card{position:absolute;z-index:60;max-width:330px;background:#FFFFFF;" +
      "border:1px solid #D8D4CA;border-radius:10px;padding:15px 17px;" +
      "box-shadow:0 6px 26px rgba(27,42,51,.16);" +
      "font:400 15px/1.5 'Iowan Old Style',Palatino,Georgia,serif;color:#25303A}" +
    ".gl-card b{display:block;font:600 13px 'Helvetica Neue',Arial,sans-serif;" +
      "letter-spacing:.06em;margin:0 0 3px;color:#1B2A33}" +
    ".gl-card i{display:block;font-style:italic;font-size:14px;color:#6E6B63;margin:0 0 8px}" +
    ".gl-card p{margin:0}" +
    ".gl-card a.more{display:inline-block;margin:11px 0 0;font:600 12px 'Helvetica Neue',Arial,sans-serif;" +
      "letter-spacing:.05em;color:#2E6473;text-decoration:none;border-bottom:1px solid #B8CBD1}" +
    "@media print{a.gl{border-bottom:0}.gl-card{display:none}}";
  document.head.appendChild(css);

  var card = null, current = null;

  function close(){
    if(card){ card.remove(); card = null; }
    if(current){ current.classList.remove("open"); current = null; }
  }

  function open(a){
    var id = (a.getAttribute("href")||"").split("#")[1];
    var g = G[id];
    if(!g) return false;
    close();
    card = document.createElement("div");
    card.className = "gl-card";
    card.innerHTML = "<b>" + g.t + "</b>"
      + (g.x ? "<i>" + g.x + "</i>" : "")
      + "<p>" + g.d + "</p>"
      + '<a class="more" href="glossary.html#' + id + '">All terms &rarr;</a>';
    document.body.appendChild(card);

    var r = a.getBoundingClientRect();
    var top = r.bottom + window.scrollY + 8;
    var left = r.left + window.scrollX;
    var w = card.offsetWidth;
    if(left + w > window.innerWidth - 14) left = window.innerWidth - w - 14;
    if(left < 10) left = 10;
    if(r.bottom + card.offsetHeight + 20 > window.innerHeight)
      top = r.top + window.scrollY - card.offsetHeight - 8;
    card.style.top = top + "px";
    card.style.left = left + "px";

    a.classList.add("open");
    current = a;
    return true;
  }

  document.addEventListener("click", function(ev){
    var a = ev.target.closest ? ev.target.closest("a.gl") : null;
    if(a){
      if(a === current){ ev.preventDefault(); close(); return; }
      if(open(a)) ev.preventDefault();
      return;
    }
    if(card && !ev.target.closest(".gl-card")) close();
  });
  document.addEventListener("keydown", function(ev){ if(ev.key === "Escape") close(); });
  window.addEventListener("resize", close);
})();
