Phase 4 Core Objectives (Q3 2025 Target)
Phase 4 transforms IHEP from a two-dimensional resource platform into a fully interactive, spatial computing environment. The primary deliverables are:
First, the OpenUSD-based digital twin viewer that renders patient health trajectories in three-dimensional space, allowing both patients and clinicians to visualize health data as spatial-temporal manifolds rather than flat charts.
Second, the three.js rendering engine that translates Universal Scene Description files into real-time, browser-accessible visualizations without requiring specialized software or hardware beyond a modern web browser.
Third, the backend digital twin service that continuously synthesizes patient data streams (wearable devices, clinical lab results, self-reported metrics) into coherent spatial representations while maintaining HIPAA compliance through the Google Cloud Healthcare API segregation you've already architected.
Fourth, the collaborative research application portal that allows qualified researchers to submit proposals for accessing de-identified digital twin data, complete with institutional review board integration and automated compliance checking.
Mathematical Foundation: Spatial Health Manifolds
Your digital twin implementation requires rigorous mathematical grounding to ensure that health data projections into three-dimensional space maintain clinical validity. The core mathematical framework operates as follows.
Define the patient health state at time t as a vector in high-dimensional physiological space. Let H(t) represent this state where H(t) = [viral_load(t), CD4_count(t), medication_adherence(t), mental_health_score(t), social_support_index(t), ...]. This vector typically exists in dimension n where n can range from 50 to 500 depending on data granularity.
The challenge becomes projecting this high-dimensional health state into three-dimensional visual space while preserving the most clinically significant relationships. This requires dimensionality reduction with clinical validity constraints.
The projection mapping Φ: R^n → R^3 must satisfy:
Φ(H(t)) = [x(t), y(t), z(t)]
where each coordinate axis represents a clinically meaningful composite dimension. The optimal projection preserves local neighborhoods in health space, meaning patients with similar health profiles should appear spatially proximate in the visualization.
We can formalize this using a constrained manifold learning approach. The objective function to minimize is:
L(Φ) = Σ(i,j) ||Φ(H_i) - Φ(H_j)||² × w_ij + λ × Clinical_Validity_Penalty(Φ)
where w_ij represents the similarity between patients i and j in the original high-dimensional health space, and the clinical validity penalty ensures that the three axes correspond to interpretable clinical constructs (for example, immune function, viral control, and quality of life).
The constraint ||∇Φ|| ≤ M ensures smooth projections without discontinuous jumps that would confuse clinical interpretation.
OpenUSD Architecture Specification
Universal Scene Description provides the industry-standard format for describing complex three-dimensional scenes with time-varying properties, which maps perfectly to your digital twin requirements where patient health evolves continuously.
Your USD file structure should follow this hierarchy. At the root level, you have the DigitalTwinStage which contains all patient twin instances. Each patient exists as a separate Xform (transformation) node that encapsulates their complete health trajectory.
Within each patient Xform, you define several hierarchical components. The HealthTrajectory node contains time-sampled position data showing how the patient's health state moves through the three-dimensional projection space over days, weeks, and months. The BiometricGeometry node contains visual representations of key metrics, such as sphere sizes that encode CD4 counts or color gradients that encode viral load ranges.
The USD temporal encoding allows you to define attributes that vary over time using the syntax:
python
float3 position.timeSamples = {
0: (0.0, 0.0, 0.0),
30: (1.2, 0.5, -0.3),
60: (2.1, 1.0, -0.2),
90: (2.8, 1.5, 0.1)
}
This represents a patient's health trajectory where the coordinates are the three-dimensional projection at days 0, 30, 60, and 90 post-diagnosis. The system automatically interpolates positions between defined time samples.
For your HIPAA compliance requirements, the USD files must never contain raw PHI. Instead, they reference anonymized patient identifiers that map back to encrypted records in the Google Cloud Healthcare API only through secure backend services that enforce access controls.
Three.js Rendering Engine Implementation
The three.js component translates USD descriptions into interactive WebGL visualizations. The rendering pipeline operates through several mathematically defined stages.
Stage one performs USD parsing where the JavaScript USD library (such as Pixar's official USD JavaScript bindings) reads the scene description and constructs an in-memory scene graph.
Stage two builds the three.js scene hierarchy. For each patient twin in the USD file, you instantiate corresponding three.js objects. A patient trajectory becomes a THREE.Line or THREE.TubeGeometry that traces the path through health space. Biometric spheres become THREE.Mesh objects with dynamically sized geometry and color-mapped materials.
Stage three implements the camera and interaction system. You want both automated "flight path" modes that guide viewers through interesting regions of the health space, and manual exploration modes where clinicians can freely navigate.
The camera animation for automated exploration follows a parameterized curve C(s) where s ∈ [0, 1] represents progress through the animation. The curve satisfies smoothness constraints to prevent motion sickness:
C(s) = B(s) + N(s) × r(s)
where B(s) is a B-spline base curve through regions of interest, N(s) is the surface normal (ensuring the camera always looks "into" the cloud of patients), and r(s) is a radial offset function that varies to provide depth perspective.
The camera orientation Q(s) (represented as a quaternion) must satisfy ||Q'(s)|| ≤ ω_max to prevent disorienting rapid rotations, where ω_max represents the maximum angular velocity tolerance (typically around 0.5 radians per second for comfortable viewing).
Backend Digital Twin Service Architecture
The backend service that generates and updates USD files operates as a continuous synthesis pipeline with several critical components.
Your data ingestion layer connects to the Google Cloud Healthcare API through FHIR endpoints to retrieve updated lab results, to wearable device APIs for continuous biometric streams, and to the PostgreSQL database for self-reported metrics and appointment adherence data.
The synthesis engine transforms this multi-modal data into the high-dimensional health state vector H(t) for each patient at each time point. This requires handling missing data, outlier detection, and temporal alignment since different data sources update at different frequencies.
The dimensionality reduction module applies the manifold learning projection Φ to compute three-dimensional positions. This computation must be incremental, meaning new data points should update the projection without requiring complete recalculation of the entire patient population's positions. This is achieved through online learning variants of manifold algorithms.
The USD generation module constructs scene descriptions with temporal samples. For computational efficiency, you don't store every time point. Instead, you sample at clinically meaningful intervals (weekly for stable patients, daily for those in acute phases) and rely on USD's built-in interpolation between samples.
The validation layer ensures clinical coherence. It checks that projected trajectories satisfy physiological constraints, such as the constraint that CD4 count cannot increase faster than the biological maximum cell proliferation rate, represented mathematically as:
dCD4/dt ≤ r_max × CD4(t) × (1 - CD4(t)/CD4_max)
where r_max is the maximum proliferation rate and CD4_max is the physiological ceiling. If a projected trajectory violates such constraints, the system flags it for clinical review before including it in the visualization.
Morphogenetic Self-Healing for Digital Twin Service
Your digital twin backend must incorporate the morphogenetic framework specified in your technical documents. The reaction-diffusion model extends to the computational health of the USD generation pipeline itself.
Define three critical signals for the digital twin service. The computation latency signal L measures how long USD generation takes relative to the target threshold (you want updates available within seconds of new data arrival, not minutes). The data completeness signal D measures what fraction of expected data streams are successfully incorporated. The clinical validity signal V measures what percentage of generated trajectories pass the physiological constraint checks.
These signals diffuse across the service's computational graph. If one patient's twin generation exhibits high latency, that signal spreads to related components (the data ingestion endpoint, the dimensionality reduction module, the USD serializer) to identify the bottleneck.
The agent policies adapt the system. The Builder agent provisions additional compute resources (scales up Cloud Run instances or increases Vertex AI GPU allocation) when L exceeds thresholds under high data completeness. The Scavenger agent quarantines problematic data sources when D drops while V remains high, indicating that a specific data stream has become unreliable.
The critical enhancement for Phase 4 is adding a Validator agent specifically for clinical coherence. This agent monitors V and when it detects systematic violations of physiological constraints, it triggers retraining of the dimensionality reduction model with additional constraint enforcement in the optimization objective.
Collaborative Research Application Portal
The research application component provides controlled access to de-identified digital twin data for qualified investigators. This requires mathematical guarantees around privacy preservation.
Your de-identification process must satisfy differential privacy constraints. When a researcher queries the digital twin dataset, the system adds calibrated noise to prevent inference of individual patient data. The noise magnitude η follows the Laplace mechanism:
η ~ Laplace(0, Δf/ε)
where Δf is the sensitivity of the query function (maximum change in output from adding or removing one patient) and ε is the privacy budget parameter. Smaller ε provides stronger privacy but reduces data utility.
For example, if a researcher requests the average CD4 count trajectory for patients in a demographic subgroup, the true average μ is perturbed to μ + η before returning. The privacy budget ε depletes with each query, and once a researcher exhausts their allocated budget, they must submit a new IRB-approved protocol for additional access.
The application portal workflow operates through several validated stages. Researchers submit proposals through a structured form capturing hypothesis, methodology, requested data variables, and IRB approval documentation. An automated classifier, trained on past successful and unsuccessful applications, provides initial triage scoring each proposal on scientific merit, feasibility, and compliance risk.
Proposals passing automated review enter manual review by your governance board. Approved researchers receive time-limited API keys with query budgets, access logging, and automatic audit trail generation.
The portal implementation should use Next.js API routes for the submission endpoint, Google Cloud Functions for the automated review pipeline, and Firestore for storing proposal status with proper access controls ensuring researchers can only view their own submissions.