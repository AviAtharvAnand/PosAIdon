# EarthEcho Water-Quality Analysis Dictionary — PosAIdon Knowledge Reference

**Source:** User-supplied workbook `Avi Copy of Earth_Echo_Analysis_Dictionary.xlsx` (described by the user as received from Cornell).
**Scope:** Interpretive reference material, **not** a validated water-quality index or an official regulatory standard.

## Instructions for using this reference

- Use these entries to explain recorded values, *possible* causes, ecological effects, recommended follow-up sampling, and potential interventions.
- Never represent a potential cause (for example, sewage, fertilizer runoff, or algal growth) as confirmed without supporting evidence.
- This document does not define or calculate an official WQI and does not establish water safety.
- Prefer location-matched actual observations returned by PosAIdon's CSV analysis over examples or generic thresholds here.
- For multi-parameter interpretations, measurements should be taken at comparable places and times; combining unrelated dates or GPS stations can mislead.
- `Z-score` ranges require a suitable historical reference distribution at the **same site and season**. If none is available, do not calculate a meaningful anomaly classification.
- In the source workbook, DO categories are stated in mg/L while some observations use ppm. Do not automatically equate units for all conditions without checking the conversion assumptions.
- Temperature lacks a universal ecological-safe threshold; the sheets include both seasonal Z-score comparisons and simplified Fahrenheit bands. Identify which source sheet/rule is being discussed.
- Turbidity JTU bands in this workbook must not be applied directly to NTU observations.
- A range or suggested action here is contextual guidance, not permission to alter a waterbody or establish regulatory compliance.

## Sheet 1 — Individual parameter rules (controlled)

### Temperature — In Range

**Range:** Z score: -1 <= z <= 1 (using historical readings at the same site and season)

**Indication:** In Range

**Meaning/Potential Cause:** Temperature in range

**Re-Testing Next Steps:** Assess seasonal temperature and trends in the area.

**Potential Interventions:** Temperature in range

**Effects:** Often no negative effects

**Considerations:** Temperature in range

**Formula:** z = (Observed temperature - Historical mean temperature) / Historical standard deviation of temperature

**Notes:** For temperature, it is important to consider the long term trends in a particular body of water as there are not universal temperature cutoffs. Could we leverage some statistical measure like standard deviation or variation to flag changes?

### Temperature — Cooler than usual

**Range:** Z score: -2 < z < -1 (using historical readings at the same site and season)

**Indication:** Cooler than usual

**Meaning/Potential Cause:** Cold runoff, cold rainfall, unusual weather, industrial cooling, topography changes leading to increased shading

**Re-Testing Next Steps:** Repeat reading at comparable time/depth; check recent rainfall and upstream inputs.

**Potential Interventions:** If persistent, trace unusually cold discharge or changed flow/shade; refer suspected permitted discharges to local water authority.

**Effects:** Cooler water can lead to changes in dissolved oxygen, chemical reaction rates, and density. It can also lead to ecosystem shifts if the change is long term, changing a species preferred habitat range and biological activity such as metabolic function and reproduction.

**Considerations:** Temperature varies naturally throughout the day, seasons, and at various depths. Various species can also have optimal water temperatures, so setting an ideal temperature is nearly impossible.

### Temperature — Unusually Cold

**Range:** Z score: z <= -2 (using historical readings at the same site and season)

**Indication:** Unusually Cold

**Meaning/Potential Cause:** Cold runoff, cold rainfall, unusual weather, industrial cooling, topography changes leading to increased shading

**Re-Testing Next Steps:** Repeat reading at comparable time/depth; check recent rainfall and upstream inputs.

**Potential Interventions:** If persistent, trace unusually cold discharge or changed flow/shade; refer suspected permitted discharges to local water authority.

**Effects:** Lower metabolic rate and lethargy in aquatic species, shift in normal location of aquatic species (if runoff water is colder than normal water temps or there has been a chance in salinity layers, deeper water can sometimes be warmer than surface water due to low mixing and more dense; denser deeper water usually stays a more consistent temp than surface water), weakens immunity of aquatic species leading to higher disease risk, can lead to decreased reproduction and even sudden thermal shock which can lead to death.

**Considerations:** Temperature varies naturally throughout the day, seasons, and at various depths. Various species can also have optimal water temperatures, so setting an ideal temperature is nearly impossible. Unusual weather patterns can often cause short term temperature changes, such as snow storms, heatwaves, or draught.

**Notes:** What are cold effects to consider?

### Temperature — Hotter than usual

**Range:** Z score: 1 < z < 2 (using historical readings at the same site and season)

**Indication:** Hotter than usual

**Meaning/Potential Cause:** Loss of vegetation, urban stormwater runoff, thermal pollution, drought, high air temperatures, climate change, impoundments, grouundwater inflow, turbidity

**Re-Testing Next Steps:** Repeat reading at comparable time/depth; measure DO, especially near dawn.

**Potential Interventions:** Restore streamside shade; reduce hot pavement/roof runoff with rain gardens and infiltration; conserve watershed water and investigate warm outfalls or industrial discharge.

**Effects:** Organisms may experience reduced or blocked sexual maturation, inhibited or blocked critical stages of larval development, reduced feeding and growth, increased susceptibility to predation, reduced productivity of macroalgae, or increased death (EPA).

**Considerations:** Temperature varies naturally throughout the day, seasons, and at various depths. Various species can also have optimal water temperatures, so setting an ideal temperature is nearly impossible.

### Temperature — Unusually Hot

**Range:** Z score: z >= 2 (using historical readings at the same site and season)

**Indication:** Unusually Hot

**Meaning/Potential Cause:** Loss of vegetation, urban stormwater runoff, thermal pollution, drought, high air temperatures, climate change, impoundments, groundwater inflow, turbidity

**Re-Testing Next Steps:** Repeat reading at comparable time/depth; measure DO, especially near dawn.

**Potential Interventions:** Restore streamside shade; reduce hot pavement/roof runoff with rain gardens and infiltration; conserve watershed water and investigate warm outfalls or industrial discharge.

**Effects:** Organisims may expereince reduced or blocked sexual maturation, inhibited or blocked critical stages of larval development, reduced feeding and growth, increased susceptibility to predation, reduced productivity of macroalgae, increased death (EPA).

**Considerations:** Temperature varies naturally throughout the day, seasons, and at various depths. Various species can also have optimal water temperatures, so setting an ideal temperature is nearly impossible. Unusual weather patterns can often cause short term temperature changes, such as snow storms, heatwaves, or draught.

### pH — In Range

**Range:** 6.5 - 9.0

**Indication:** In Range

**Meaning/Potential Cause:** pH in range

**Re-Testing Next Steps:** Assess seasonal pH and trends in the area.

**Potential Interventions:** pH in range

**Effects:** Often no negative effects

**Considerations:** Different organisms vary greatly in the pH ranges they can tolerate. As pH becomes untolerable, some organisms may die off or begin to avoid water. Further, it is important to consider that although a species may be able to tolerate a pH level, its food source may not be able to.

### pH — Too low (acidic)

**Range:** <6.5 OR Z-score <-2 (compared to historical readings at same location and season)

**Indication:** Too low (acidic)

**Meaning/Potential Cause:** Acid rain, mining pollution, decomposition, changes in watershed chemistry, coal storage, landfills (under certain conditions), and some fertilizers

**Re-Testing Next Steps:** Confirm with calibrated meter in both morning and afternoon; repeat upstream/downstream and check rain, drainage, and runoff.

**Potential Interventions:** Reduce excess fertilizer inputs and manage acidic runoff; investigate mine, landfill, or industrial sources with local water authorities. Do not add chemicals to neutralize the water. Avoid abrupt changes.

**Effects:** Damage of fish gills, fins, and exoskeletons; harms fish egg viability which can lead to loss of senstivie species and biodiversity. Higher acidity can lead to the conversion of mercury into methlymercury (a neurotoxin) that can build up through the food web leading to disease and death.

**Considerations:** Active photosynthesis by algae or aquatic plants consumes CO₂ and can drive pH up during the day, dropping overnight as respiration adds CO₂

**Notes:** If we cannot establish a historical distribution could we bootstrap one with season, location, and nearby readings.

### pH — Too high (alkaline)

**Range:** >9.0 OR Z-score >2 (compared to historical readings at same location and season)

**Indication:** Too high (alkaline)

**Meaning/Potential Cause:** Lawn lime, alkaline algae, industrial discharge, construction runoff, metal processing, limestone processing

**Re-Testing Next Steps:** Confirm with calibrated meter in both morning and afternoon; assess algae and paired DO/turbidity.

**Potential Interventions:** Prevent lawn-lime, concrete washout, and construction runoff; reduce nitrogen/phosphorus inputs. Report persistent extreme pH or suspected industrial discharges; avoid chemical dosing. Avoid abrupt changes.

**Effects:** Damage of fish gills, fins, and exoskeletons; harms fish egg viability which can lead to loss of senstivie species and biodiversity. High pH can lead nitrogen balance towards unionized ammonia which is very toxic to aquatic organisms.

**Considerations:** Active photosynthesis by algae or aquatic plants consumes CO₂ and can drive pH up during the day, dropping overnight as respiration adds CO₂. Hard/mineral-rich source water, limestone, coral rock, shells, and unsealed cement can raise pH. Higher pH can lead to higher unionized ammonia which becomes especially toxic when paried with warmer water.

**Notes:** Could we add a section to the readings, where the user can include notes on what they think may be causing the change? How does high v. low pH affect fish differently?

### Turbidity — Excellent

**Range:** 0 JTU OR Z score within -1 < x< 1

**Indication:** Excellent

**Meaning/Potential Cause:** Turbidity in range

**Re-Testing Next Steps:** Turbidity in range

**Potential Interventions:** Turbidity in range

**Effects:** Often no negative effects

**Considerations:** Turbidity in range

**Notes:** Is clear water when the water historically has sediment something of value that is missed by this analysis?

### Turbidity — Good

**Range:** 1-40 JTU OR Z score within -1 < x < 1

**Indication:** Good

**Meaning/Potential Cause:** Turbidity in range

**Re-Testing Next Steps:** Continue routine monitoring; compare turbidity with rainfall and site history.

**Potential Interventions:** Inspect nearby banks, storm drains, and disturbed soil if readings trend upward.

**Effects:** Often no negative effects

**Considerations:** Turbidity in range

### Turbidity — Fair

**Range:** 41-100 JTU OR 1 < z <2

**Indication:** Fair

**Meaning/Potential Cause:** Precipitation runoff, disruption of bottom sediment, small floating organisms, dead organic matter, wood ash from wildfires, spring snowmelt, summer algal growth, contstruction, farming, forestry, urban runoff, untreated wastewater (EPA).

**Re-Testing Next Steps:** Resample after rain and during dry weather

**Potential Interventions:** Install erosion-control measures at new lawns/construction, reduce overwatering and driveway runoff, use rain gardens/vegetated buffers; inspect for algae or wastewater if turbidity remains high.

**Effects:** Clogging fish gills, hindering visibility, decreasing light penetration into water, decreasing photosythesis, reducing fish resistence to disease, alter egg and larval development. High turbidity can harm the surrounding ecosystem in several ways. Floating particles like silt, algae, and organic matter block sunlight from reaching underwater plants, which prevents them from making the oxygen fish need to survive. As excess sediment settles to the bottom, it can bury fish eggs and bottom-dwelling organisms, while suspended particles can irritate or clog fish gills.

**Considerations:** High turbidity water is often darker and cloudier which absorbs more heat from the sun, warming the waterway and lowering oxygen. Additionally, runoff that causes high turbidity often carries harmful pollutants (eg, fertilizers, bacteria, and chemicals) into the water.

### Turbidity — Poor

**Range:** >100 JTU OR Z-score >2 (compared to historical readings at same location and season)

**Indication:** Poor

**Meaning/Potential Cause:** Precipitation runoff, disruption of bottom sediment, small floating organisms, dead organic matter, wood ash from wildfires, spring snowmelt, summer algal growth, contstruction, farming, forestry, urban runoff, untreated wastewater (EPA). Construction and land clearing, dam release, and other human activity distruptions.

**Re-Testing Next Steps:** Resample both upstream and downstream after rain and during dry weather

**Potential Interventions:** Inspect construction, sediment plumes, sewage, and algae. Stabilize exposed soils/banks, install sediment barriers and stormwater controls; notify responsible authority for persistent/severe pollution.

**Effects:** Clogging fish gills, hindering visibility, decreasing light penetration into water, decreasing photosythesis, reducing fish resistence to disease, alter egg and larval development. High rate of sedimentation can also lead to alteration of stream beds and can affect flood control.

**Considerations:** High turbidity can often be due to extreme events such as rapid snow/ice melt, bank collapse or landslides, and wildlife. Often turbidty can rise quickly after these events, but then will settle and come back into normal parameters.

### Dissolved Oxygen — Very Low

**Range:** <3 mg/L OR Z-score <-2 (compared to historical readings at same location and season)

**Indication:** Very Low

**Meaning/Potential Cause:** Fertilizer runoff, sewage contamination, elevated water temperature, slow-moving water, organic matter, algal blooms (night), poorly maintaned septic systems, tree removal, water dam, vertical mixing blocked by layers of salt and freshwater

**Re-Testing Next Steps:** Repeat DO at dawn and afternoon and record temperature. CHECK FOR FISH DISTRESS

**Potential Interventions:** Investigate sewage, organic loading, blooms and stagnation. Temporary aeration only under professional/site-manager direction.

**Effects:** Low oxygen conditions can place fish in distress, and in anoxic (no oxygen) conditons, we can even start to see fish death (EPA). Even brief drops in oxygen can slow growth, impair reproduction, cause developmental issues, and lead to weakened immune systems in aquatic orgamisms. Extremely low oxygen levels often lead to 'dead zones' where large areas of water can not support aquatic life.

**Considerations:** DO varies seasonally and daily. After spring and fall turnover, DO is generally the same throughout the body of water. Summer and winter stratification, deeper water can have lower DO, which is not as supportive to marine life. In terms of daily variation, DO is lowest in the early morning, as photosynthesis ceases overnight and animals still require oxygen. There is not one universal DO level; however, a trend that emerged out of the EPA data is that coldwater bodies need higher DO on average

### Dissolved Oxygen — Low

**Range:** 3 <= DO < 5 mg/L

**Indication:** Low

**Meaning/Potential Cause:** Fertilizer runoff, sewage contamination, elevated temperature, slow-moving water, organic matter, algal blooms (night), poorly maintained septic systems, tree removal

**Re-Testing Next Steps:** Repeat DO at dawn and afternoon and record temperature.

**Potential Interventions:** Check fertilizer, yard waste, manure and septic inputs; stop nutrient/organic runoff, restore vegetated buffers and shade, and investigate stagnant flow or decaying algal blooms.

**Effects:** Low oxygen conditions can place fish in distress, and in anoxic (no oxygen) conditons, we can even start to see fish death (EPA). Even brief drops in oxygen can slow growth, impair reproduction, cause developmental issues, and lead to weakened immune systems in aquatic orgamisms.

**Considerations:** DO varies seasonally and daily. After spring and fall turnover, DO is generally the same throughout the body of water. Summer and winter stratification, deeper water can have lower DO, which is not as supportive to marine life. In terms of daily variation, DO is lowest in the early morning, as photosynthesis ceases overnight and animals still require oxygen.

**Notes:** Time of day matters, especially for algae. Consider incorporating percent saturation.

### Dissolved Oxygen — Good

**Range:** 5 <= DO <= 8 mg/L

**Indication:** Good

**Meaning/Potential Cause:** DO in range

**Re-Testing Next Steps:** Assess seasonal trends and usual DO measurements in the area

**Potential Interventions:** DO in range

**Effects:** Often no negative effects

**Considerations:** DO varies seasonally and daily. After spring and fall turnover, DO is generally the same throughout the body of water. Summer and winter stratification, deeper water can have lower DO, which is not as supportive to marine life. In terms of daily variation, DO is lowest in the early morning, as photosynthesis ceases overnight and animals still require oxygen.

### Dissolved Oxygen — High

**Range:** >8 mg/L OR Z-score >2 (compared to historical readings at same location and season)

**Indication:** High

**Meaning/Potential Cause:** Cold water temperatures, fast-flowing water, nutrient enrichment, high photosynthetic activity, artificial aearation, high sunlight, excessive algae growth (day), low salinity

**Re-Testing Next Steps:** Repeat DO at dawn and afternoon and record temperature.

**Potential Interventions:** High DO can be natural. If strong daytime peaks accompany high pH/turbidity, assess algae and nutrients and reduce fertilizer/wastewater runoff; avoid unnecessary aeration.

**Effects:** Often no negative effects

**Considerations:** DO varies seasonally and daily. After spring and fall turnover, DO is generally the same throughout the body of water. Summer and winter stratification, deeper water can have lower DO, which is not as supportive to marine life. In terms of daily variation, DO is lowest in the early morning, as photosynthesis ceases overnight and animals still require oxygen. Highly oxygenated or turbulent waters can lead to stress on aquatic organisms; watch for sustained high DO or extreme fluctuations.

## Sheet 2 — Interacting parameter combinations

**Important:** The rules below identify *possible* interpretations and follow-up actions. They are not causal diagnoses. Only apply them where paired observations support the same time and location.

### Temperature High, DO Low

**Potential issues (hypotheses):** Thermal Pollution; Drought Conditions; Stagnant Water

**Potential Interpretation:** Warm water may have reduced oxygen availability, potentially creating stressful conditions for aquatic life.

**Re-Testing Next Steps:** Verify temperature and DO at matched sites/times, with a preference for dawn for DO readings (DO is lowest) and a preference for midafternoon for temperature. Check low flow and warm outfalls.

**Potential Interventions:** Restore riparian shade, reduce heated urban stormwater through infiltration or rain gardens, investigate any thermal discharges (such as power plants). Alert to local wildlife authorities if wildlife are clearly disstressed.

**Interaction Notes:** Due to increase heat absorption of water and light penetration (EPA)

### Turbidity High, DO Low

**Potential issues (hypotheses):** Heavy runof after storms; Erosion; Nutrient and organic matter loading

**Potential Interpretation:** Suspended material and oxygen depletion may be associated with runoff, organic loading, or separate processes.

**Re-Testing Next Steps:** Repeat turbidity and DO after rain and in dry weather

**Potential Interventions:** Determine if the problem is temporary stormwater runoff or a signal to something more persistent; check sediment versus organic particles. Stabilize disturbed ground and banks if possible; add erosion controls, vegetation and stormwater retention. Investigate sewage, manure and fertilizer sources if low DO persists after repeat testing.

### pH High, Temperature High, DO Low

**Potential issues (hypotheses):** Eutrophication; Excessive Algae Growth

**Potential Interpretation:** Warm, oxygen-stressed conditions with elevated pH. Biological activity may be involved, but the combination alone doesn't establish eutrophication.

**Re-Testing Next Steps:** Measure dawn/afternoon DO and pH and look for blooms

**Potential Interventions:** Establish daily changes due to natural biological processes; test nitrogen/phosphorus when feasible. Reduce lawn/agricultural fertilizer and wastewater/septic nutrient inputs; restore vegetated buffers, manage stormwater. Alert to local wildlife authorities if wildlife are clearly disstressed.

**Interaction Notes:** As photosynthesis occurs, pH may increase throughout the day. At night, as photosynthesis ceases, pH decreases.

### Turbidity High, pH High

**Potential issues (hypotheses):** Algae Bloom; Concrete/Construction Runoff; Alkaline soils or sediments

**Potential Interpretation:** Suspended particles combined with alkaline conditions may reflect biological growth or an alkaline runoff source

**Re-Testing Next Steps:** Check whether cloudiness is algal (green) versus mineral sediment; sample pH/DO at dawn and afternoon.

**Potential Interventions:** Reduce nutrient runoff, repair septic leaks and improve vegetated buffers; use erosion controls if sediment is responsible. Report harmful-bloom indicators.

### pH Low, DO Low

**Potential issues (hypotheses):** Acid Mine Drainage; Industrial Contamination; Organic Pollution

**Potential Interpretation:** Acidic and oxygen depleted conditions could indicate multiple stressors of a shared source

**Re-Testing Next Steps:** Confirm pH and DO and sample upstream/downstream before and after a suspected pollution source;

**Potential Interventions:** Consider metals, conductivity, nutrients and microbial testing. Investigate mine/industrial discharge, wastewater/septic leaks and decaying organics; control the identified source. Alert to local wildlife authorities if wildlife are clearly disstressed

### pH High, DO High

**Potential issues (hypotheses):** Elevated Photosynthetic Activity; Possible Nutrient Enrichment; Large Daily Oxygen Swings

**Potential Interpretation:** Daytime photosynthesis can raise both pH and DO. This can reflect natural plant activity or excessive algal growth; high afternoon values alone are not necessarily a cause for concern

**Re-Testing Next Steps:** Retest pH and DO just before dawn and mid-to-late afternoon at the same location. Check for low predawn DO, unusually large swings, visible algae, and visible nearby nutrient sources.

**Potential Interventions:** If repeated swings are excessive, investigate potential fertilizer, manure, or septic contamination; reduce nutrient runoff and protect vegetated buffers. Report suspected harmful blooms to local authorities.

### pH Low, Turbidity High

**Potential issues (hypotheses):** Acidic Stormwater Runoff; Disturbed Acidic Soils; Industrial or Mine Drainage

**Potential Interpretation:** Acidic inputs and suspended particles can come from storms or other disturbances, but the two changes can also have unrelated causes.

**Re-Testing Next Steps:** Retest pH and turbidity. Compare wet- and dry-weather samples upstream and downstream of exposed soil, construction, storm drains, or potential discharge points.

**Potential Interventions:** Stabilize exposed soil, control erosion and stormwater flows, and investigate any persistent acidic discharge. Refer possible mine or industrial contamination to local authorities.

### Temperature Low, DO Low

**Potential issues (hypotheses):** Oxygen-Consuming Organic Matter; Low-Oxygen Groundwater; Water Column Stratification

**Potential Interpretation:** Cold water generally has greater oxygen solubility; unusually low DO may reflect oxygen consumption, oxygen-poor groundwater, or mixing from low-oxygen depths.

**Re-Testing Next Steps:** Retest both measurements at comparable times and depths (predawn is a candiate option); calculate DO percent saturation when possible. Sample upstream/downstream and inspect slow-flowing reaches or potential groundwater inputs.

**Potential Interventions:** Investigate organic waste and wastewater inputs or stagnant conditions. Address pollution sources and restore natural flow or riparian habitat where appropriate; report observed fish distress to local authorities.

### Temperature High, Turbidity High

**Potential issues (hypotheses):** Warm Stormwater Runoff; Sediment Erosion; Land Disturbance

**Potential Interpretation:** Warm runoff from pavement or disturbed surfaces can carry sediment. Turbid water may also warm from sunlight, but simultaneous increases are not specific to any one source.

**Re-Testing Next Steps:** Retest before and after rainfall at similar times of day. Compare upstream/downstream of paved surfaces, building sites, and storm drains; check whether both indicators subside after storms.

**Potential Interventions:** Control erosion and exposed soil; support infiltration, vegetated swales, rain gardens, and streamside shade where appropriate. Trace persistent hot or turbid outfalls.

### Temperature High, DO High

**Potential issues (hypotheses):** Strong Daytime Photosynthesis; High Aeration; Possible Oxygen Supersaturation

**Potential Interpretation:** High DO despite warmer water can arise from daytime oxygen production or turbulent aeration. Interpret against DO percent saturation, rather than mg/L alone.

**Re-Testing Next Steps:** Repeat DO, pH, and temperature near dawn and mid-to-late afternoon. Calculate percent saturation and check for pronounced day-night oxygen or pH swings.

**Potential Interventions:** If large oxygen swings indicate excess productivity, investigate and reduce nutrient runoff; otherwise continue monitoring and document normal seasonal or rapid-water aeration effects.

### Turbidity Low, DO Low

**Potential issues (hypotheses):** Stagnant or Poorly Mixed Water; Decomposition; Depth-Related Oxygen Depletion

**Potential Interpretation:** Clear water can still be oxygen-poor because of microbial respiration, slow mixing, or depleted deeper layers; visual clarity is not evidence of adequate oxygen.

**Re-Testing Next Steps:** Repeat DO near dawn at comparable depth and time. If safe and feasible, compare surface and deeper samples; note flow restrictions, accumulated vegetation, and decaying material.

**Potential Interventions:** Investigate organic waste, sewage, and restricted flow. Address identified sources and avoid disturbing oxygen-poor sediments; alert local authorities if there are signs of visible distress.

### pH Low, DO High

**Potential issues (hypotheses):** Naturally Acidic Water; Acidic Runoff; Strong Aeration

**Potential Interpretation:** Acidic water may still be well oxygenated due to mixing, cool water, or photosynthesis. The low pH and high DO may have separate causes rather than a common contaminant.

**Re-Testing Next Steps:** Repeat pH and DO and compare with historical site data at matching times. Check upstream/downstream, recent rain, local geology or wetlands; review DO percent saturation.

**Potential Interventions:** Avoid intervening solely because DO is high. Trace persistent unexplained acidity, including runoff or industrial sources; seek advice from authorities where aquatic life is at risk. Check for abnormal swings.

## Sheet 3 — Individual parameter raw-value reference bands

**Important:** These are simplified bands transcribed from the source workbook; they are not universal environmental standards. Note that source unit conventions can differ from the CSV columns.

### Temperature — In Range

**Range:** 68-86 F

**Notes:** For temperature, it is important to consider the long term trends in a particular body of water as there are not universal temperature cutoffs. Could we leverage some statistical measure like standard deviation or variation to flag changes?

### Temperature — Too cold

**Range:** <68 F

**Meaning/Potential Cause:** Cold runoff, cold rainfall, unusual weather, industrial cooling, topography changes leading to increased shading

### Temperature — Too hot

**Range:** >86 F

**Meaning/Potential Cause:** Loss of vegetation, urban stormwater runoff, thermal pollution, drought, high air temperatures, climate change, impoundments, grouundwater inflow, turbidity

**Notes:** Reduced or blocked sexual maturation, inhibited or blocked critical stages of larval development, reduced feeding feeding anf growth, increased susceptibility to predation, reduced productivity of macroalgae, increased death (EPA).

### pH — In Range

**Range:** 6.5 - 9.0

### pH — Too low (acidic)

**Range:** <6.5

**Meaning/Potential Cause:** Acid rain, mining pollution, decomposition, changes in watershed chemistry, coal storage, landfills (under certain conditions), and some fertilizers

### pH — Too high (alkaline)

**Range:** >9.0

**Meaning/Potential Cause:** Lawn lime, alkaline algae, industrial discharge, construction runoff, metal processing, limestone processing

**Notes:** Could we add a section to the readings, where the user can include notes on what they think may be causing the change

### Turbidity — Excellent

**Range:** 0 JTU

### Turbidity — Good

**Range:** 1-40 JTU

### Turbidity — Fair

**Range:** 41-100 JTU

### Turbidity — Poor

**Range:** >100 JTU

**Meaning/Potential Cause:** Soil erosion, stormwater runoff, algal blooms, wastewater discharge, installing a new lawn, home construction, driveway installation, lawn overwatering, pesticides, mining, logging, excavation

### Dissolved Oxygen — Very Low

**Range:** <3 mg/L

**Meaning/Potential Cause:** See below

### Dissolved Oxygen — Low

**Range:** 3-5 mg/L

**Meaning/Potential Cause:** Fertilizer runoff, sewage contamination, elevated temperature, slow-moving water, organic matter, algal blooms (night), poorly maintaned septic systems, tree removal

**Notes:** Time of day matters, especially for algae

### Dissolved Oxygen — Good

**Range:** 5-8 mg/L

### Dissolved Oxygen — High

**Range:** >8 mg/ML

**Meaning/Potential Cause:** Cold water temperatures, fast-flowing water, nutrient enrichment, high photosynthetic activity, artificial aearation, high sunlight, excessive algae growth (day)

## Notes for PosAIdon

1. When the user asks what a specific measurement means, start with the actual data, then use the corresponding controlled rule as contextual interpretation.
2. When a question concerns two or three parameters, look up their combination rule, but confirm all readings are paired by date and site before relating them.
3. If the user asks for WQI, this dictionary cannot by itself produce a certified numeric WQI. Use an explicitly specified methodology with objectives, unit handling, and sufficiency checks.
4. If sources conflict or a threshold is ambiguous, state the uncertainty rather than inventing a rule.
