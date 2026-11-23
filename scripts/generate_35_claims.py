import json
import hashlib
from pathlib import Path

def h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

claims = [
    # =========================================================================
    # 20 VERIFIED CLAIMS
    # =========================================================================
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "AlphaGenome v2 Release Announcement",
        "description": "Google DeepMind officially released AlphaGenome v2 on October 15, 2026, introducing full-genome non-coding variant impact scoring.",
        "criteria": "Official press release or scientific publication confirming AlphaGenome v2 release date and non-coding variant prediction capabilities.",
        "evidence": [
            {
                "source_url": "https://deepmind.google/discover/blog/alphagenome-v2",
                "mock_content": "October 15, 2026: DeepMind announces AlphaGenome v2, a state-of-the-art model for full-genome non-coding variant impact prediction.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["DeepMind announcement confirms release date of October 15, 2026 and variant scoring capability."],
        "contradictions": [],
        "explanation": "External press release matches title, date, and functional scope."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "Ethereum Dencun EIP-4844 Upgrade Mainnet Activation",
        "description": "Ethereum mainnet successfully activated proto-danksharding (EIP-4844) introducing blob-carrying transactions to reduce L2 transaction fees.",
        "criteria": "Ethereum Foundation consensus specification and blockchain block explorer telemetry confirming epoch activation.",
        "evidence": [
            {
                "source_url": "https://blog.ethereum.org/2026/dencun-mainnet-upgrade",
                "mock_content": "Epoch 269568 successfully finalized with EIP-4844 proto-danksharding blobs enabled across all executing nodes.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["Ethereum Foundation bulletin confirms epoch finalization with blob transactions active."],
        "contradictions": [],
        "explanation": "Consensus finalization confirmed by official network upgrade bulletin."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "NASA Europa Clipper Trajectory Insertion",
        "description": "NASA JPL mission control confirmed successful trajectory injection of Europa Clipper en route to Jupiter's icy moon.",
        "criteria": "Official NASA Jet Propulsion Laboratory mission bulletin confirming spacecraft separation and orbital parameter acquisition.",
        "evidence": [
            {
                "source_url": "https://www.jpl.nasa.gov/news/europa-clipper-trajectory-confirmed",
                "mock_content": "Mission Control at NASA JPL confirmed Europa Clipper acquired two-way communication and entered planned Mars gravity-assist trajectory.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["JPL confirmation of two-way telemetry and planned trajectory insertion."],
        "contradictions": [],
        "explanation": "Spacecraft telemetry validates successful launch and interplanetary injection."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "CERN High-Luminosity LHC Quadrupole Magnet Milestone",
        "description": "CERN verified the successful operational test of prototype Nb3Sn superconducting quadrupole magnets reaching 11.8 Tesla.",
        "criteria": "CERN technical preprint or official accelerator progress report confirming nominal 11.8 Tesla magnetic field without quench.",
        "evidence": [
            {
                "source_url": "https://home.cern/news/technical/hl-lhc-magnet-test-118t",
                "mock_content": "Technical Note: The HL-LHC inner triplet Nb3Sn quadrupole achieved and maintained 11.8 Tesla operating field under 1.9 Kelvin refrigeration.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["CERN technical note records 11.8 T sustained field at 1.9 K."],
        "contradictions": [],
        "explanation": "Scientific experimental report validates the magnetic field benchmark."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "WHO Malaria Vaccine R21/Matrix-M Distribution Target",
        "description": "The World Health Organization confirmed deployment of over 5 million doses of the R21/Matrix-M malaria vaccine across high-burden African regions.",
        "criteria": "Official WHO health directive or Gavi vaccine rollout bulletin validating milestone.",
        "evidence": [
            {
                "source_url": "https://www.who.int/news/item/malaria-r21-deployment-milestone",
                "mock_content": "Geneva: WHO and Gavi announce cumulative delivery exceeding 5.2 million doses of R21/Matrix-M to Central and West African health ministries.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["Official WHO/Gavi report documents 5.2 million doses delivered."],
        "contradictions": [],
        "explanation": "International health organization statistics confirm threshold exceeded."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "Alliance for OpenUSD Core Specification v1.0 Standard",
        "description": "AOUSD published the official OpenUSD Core Specification v1.0 standardizing interoperability for 3D computer graphics ecosystems.",
        "criteria": "Official AOUSD technical committee publication confirming release of Core Specification v1.0.",
        "evidence": [
            {
                "source_url": "https://aousd.org/specifications/core-v1-announcement",
                "mock_content": "The Alliance for OpenUSD (AOUSD) officially ratifies and releases the OpenUSD Core Specification v1.0 as an open multi-industry standard.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["AOUSD steering committee ratified and published Core Specification v1.0."],
        "contradictions": [],
        "explanation": "Official standards body ratification document confirms release."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "NOAA Arctic Sea Ice Minimum Extent Record",
        "description": "National Snow and Ice Data Center satellite telemetry recorded the 2026 annual minimum Arctic sea ice extent at 4.28 million square kilometers.",
        "criteria": "NSIDC official sea ice index analysis confirming exact measured extent value.",
        "evidence": [
            {
                "source_url": "https://nsidc.org/arcticseaicenews/2026/annual-minimum-report",
                "mock_content": "NSIDC Arctic Sea Ice News: Sea ice extent reached its annual minimum of 4.28 million sq km on September 18, 2026.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["NSIDC telemetry records 4.28 million sq km on September 18, 2026."],
        "contradictions": [],
        "explanation": "Satellite telemetry directly corroborates stated metric."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "ISO/IEC 42001 Artificial Intelligence Management Certification",
        "description": "Enterprise software provider CloudCore passed formal third-party audit and achieved ISO/IEC 42001:2023 AI Management certification.",
        "criteria": "Accredited certification body certificate and public directory record verifying ISO/IEC 42001 compliance.",
        "evidence": [
            {
                "source_url": "https://certificates.bsigroup.com/directory/cloudcore-iso42001",
                "mock_content": "BSI Directory Verification: CloudCore Inc. holds valid Certificate AI-784019 in conformance with ISO/IEC 42001:2023.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["Accredited registrar confirms valid certificate under ISO/IEC 42001:2023."],
        "contradictions": [],
        "explanation": "Official registrar certificate directory confirms compliance."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "Solana Firedancer Validator Testnet Performance Milestone",
        "description": "Jump Crypto demonstrated the independent Firedancer C++ validator client sustaining 1,000,000 transactions per second in testnet environment.",
        "criteria": "Public benchmark repository release and independent testnet telemetry log confirming sustained 1M TPS throughput.",
        "evidence": [
            {
                "source_url": "https://firedancer.jumpcrypto.com/benchmarks/testnet-1m-tps",
                "mock_content": "Testnet Run #409: Firedancer achieved sustained synthetic load of 1,024,000 TPS with sub-400ms block production.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["Engineering telemetry records 1,024,000 TPS under testnet conditions."],
        "contradictions": [],
        "explanation": "Telemetry benchmark validates the 1M TPS performance milestone."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "CRISPR Cas12a Sickle Cell Phase III Clinical Endpoint",
        "description": "Therapeutics consortium reported Phase III trial results where 94% of severe sickle cell patients experienced zero vaso-occlusive crises for 12 months.",
        "criteria": "Peer-reviewed medical publication or clinical trial registry final results confirming >=90% crisis-free rate.",
        "evidence": [
            {
                "source_url": "https://www.nejm.org/doi/10.1056/NEJMoa2604112",
                "mock_content": "Primary Endpoint: 47 of 50 evaluable patients (94.0%) achieved complete absence of severe vaso-occlusive crises over 12 consecutive months.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["NEJM publication documents 94.0% crisis-free patient response."],
        "contradictions": [],
        "explanation": "Peer-reviewed medical trial results confirm primary clinical endpoint."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "Google DeepMind AlphaFold 3 Biomolecular Complex Modeling",
        "description": "AlphaFold 3 demonstrated atomic-level prediction accuracy for protein interactions with DNA, RNA, ligands, and post-translational modifications.",
        "criteria": "Nature scientific research paper validating structural prediction accuracy across diverse biomolecular interaction classes.",
        "evidence": [
            {
                "source_url": "https://www.nature.com/articles/s41586-024-alphafold3-joint",
                "mock_content": "AlphaFold 3 demonstrates substantial accuracy gains in modeling protein complexes with nucleic acids, small molecule ligands, and chemical modifications.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["Nature paper confirms joint biomolecular structural prediction capabilities."],
        "contradictions": [],
        "explanation": "Peer-reviewed publication validates the multimolecular predictive model."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "Tokenized US Treasury Bills Market Cap Milestone",
        "description": "On-chain tokenized US short-term Treasury bill instruments exceeded $2.5 billion in total circulating market capitalization.",
        "criteria": "RWA.xyz aggregated on-chain registry and DTCC tokenization telemetry verifying cumulative circulating supply.",
        "evidence": [
            {
                "source_url": "https://app.rwa.xyz/treasuries/summary-2026",
                "mock_content": "Tokenized Treasuries Dashboard: Total circulating value of public blockchain US Treasury tokens crossed $2,580,000,000.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["On-chain registry confirms $2.58B circulating volume across tokenized Treasuries."],
        "contradictions": [],
        "explanation": "Independent analytics provider validates market capitalization milestone."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "ITER Fusion Reactor Vacuum Vessel Sector Sub-Assembly",
        "description": "ITER Organization confirmed completion of sector sub-assembly for the central tokamak vacuum vessel at Saint-Paul-les-Durance.",
        "criteria": "Official ITER Council progress communique confirming sector lifting and alignment in the assembly hall.",
        "evidence": [
            {
                "source_url": "https://www.iter.org/newsline/sector-assembly-milestone",
                "mock_content": "ITER Newsline: Sector Module #6 was successfully transferred and docked into the tokamak pit, meeting millimeter-precision alignment.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["ITER Newsline confirms Sector Module #6 docked in tokamak pit."],
        "contradictions": [],
        "explanation": "Official international research facility communique validates assembly completion."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "Falcon Heavy Synchronous Drone Ship Recovery",
        "description": "SpaceX successfully recovered both Falcon Heavy side-boosters simultaneously on autonomous drone ships in the Atlantic Ocean.",
        "criteria": "Federal Aviation Administration launch license telemetry and SpaceX mission webcast flight logs.",
        "evidence": [
            {
                "source_url": "https://www.spacex.com/launches/mission-fh-recovery-log",
                "mock_content": "Boosters B1089 and B1090 completed simultaneous touchdown on droneships 'A Shortfall of Gravitas' and 'Just Read the Instructions'.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["Mission log records dual simultaneous booster touchdowns on designated drone ships."],
        "contradictions": [],
        "explanation": "Flight logs and official launch operator telemetry verify dual recovery."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "Chainlink CCIP Cumulative Transaction Volume",
        "description": "Chainlink Cross-Chain Interoperability Protocol (CCIP) surpassed $10 billion in cumulative cross-chain value transferred.",
        "criteria": "DefiLlama bridge analytics and Chainlink on-chain explorer telemetry confirming aggregate volume.",
        "evidence": [
            {
                "source_url": "https://defillama.com/bridges/chainlink-ccip",
                "mock_content": "DefiLlama Metrics: Chainlink CCIP all-time routed cross-chain volume reached $10,420,000,000 across 12 supported mainnet chains.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["DefiLlama metrics record $10.42B cumulative volume across 12 chains."],
        "contradictions": [],
        "explanation": "Aggregated on-chain protocol metrics confirm target volume exceeded."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "NIST Post-Quantum Cryptography FIPS Standards Publication",
        "description": "The National Institute of Standards and Technology formally published FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA) as official federal standards.",
        "criteria": "Federal Register notice and NIST Computer Security Resource Center publication of finalized FIPS documents.",
        "evidence": [
            {
                "source_url": "https://csrc.nist.gov/publications/detail/fips/203/final",
                "mock_content": "NIST CSRC: Federal Information Processing Standards (FIPS) 203 Module-Lattice-Based Key-Encapsulation Mechanism is officially released as final.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["NIST CSRC confirms official publication of final FIPS 203 and 204."],
        "contradictions": [],
        "explanation": "Official US government standards publication confirms regulatory finalization."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "OECD Global Minimum Corporate Tax Enforcement",
        "description": "Over 140 countries began domestic legislative enforcement of the OECD Pillar Two 15% minimum corporate tax framework.",
        "criteria": "OECD International Tax Reform progress monitor verifying enacted jurisdiction count.",
        "evidence": [
            {
                "source_url": "https://www.oecd.org/tax/beps/pillar-two-implementation-summary",
                "mock_content": "OECD Report: 142 jurisdictions of the Inclusive Framework have enacted or introduced domestic legislation for the 15% GloBE minimum tax.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["OECD report documents 142 jurisdictions enacting Pillar Two legislation."],
        "contradictions": [],
        "explanation": "OECD international treaty database confirms qualifying jurisdiction count."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "WebKit WebAssembly Garbage Collection Enablement",
        "description": "Apple WebKit engineering enabled Wasm GC (Garbage Collection) by default across Safari browser builds to support Kotlin and Dart runtimes.",
        "criteria": "Official WebKit feature status repository commit and release notes.",
        "evidence": [
            {
                "source_url": "https://webkit.org/blog/wasm-gc-default-release",
                "mock_content": "WebKit Feature Status: WebAssembly Garbage Collection (WasmGC) is now enabled by default in WebKit trunk and Safari Technology Preview.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["WebKit engineering notes confirm WasmGC enabled by default in trunk."],
        "contradictions": [],
        "explanation": "Browser engine official release announcement confirms feature activation."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "Tesla Megapack 400MWh Moss Landing BESS Expansion",
        "description": "Pacific Gas and Electric interconnected an additional 400 MWh of Tesla Megapack battery storage at the Moss Landing substation.",
        "criteria": "California ISO (CAISO) grid interconnection queue and commercial operation declaration.",
        "evidence": [
            {
                "source_url": "https://www.caiso.com/market/moss-landing-phase3-cod",
                "mock_content": "CAISO Grid Operations: Commercial Operation Date (COD) certified for Moss Landing BESS Phase 3 adding 400 MWh nominal capacity.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["CAISO operations notice certifies COD for 400 MWh expansion."],
        "contradictions": [],
        "explanation": "Grid operator regulatory filing confirms interconnection and commercial operation."
    },
    {
        "scenario": "VERIFIED_CLAIM",
        "title": "Unicode 16.0 Specification Release",
        "description": "The Unicode Consortium officially released Unicode Standard Version 16.0, adding 5,185 new characters and 7 new scripts.",
        "criteria": "Official Unicode Consortium press release and character code chart specification.",
        "evidence": [
            {
                "source_url": "https://home.unicode.org/announcements/unicode-16-0-released",
                "mock_content": "Unicode Standard Version 16.0 is now available, adding 5,185 characters for modern and historical scripts, plus new emoji symbols.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "VERIFIED",
        "supporting_facts": ["Unicode Consortium announcement confirms Version 16.0 with 5,185 new characters."],
        "contradictions": [],
        "explanation": "Official standards organization release announcement confirms parameters."
    },

    # =========================================================================
    # 9 REJECTED CLAIMS
    # =========================================================================
    {
        "scenario": "REJECTED_CLAIM",
        "title": "Ambient Pressure Room-Temperature Superconductor Discovery",
        "description": "Lab preprint claimed synthesized modified lead-apatite crystals exhibited zero electrical resistance at 310 Kelvin and ambient pressure.",
        "criteria": "Independent multi-institution crystallographic and magnetic susceptibility confirmation of zero resistivity.",
        "evidence": [
            {
                "source_url": "https://arxiv.org/abs/2602.superconductor-independent-audit",
                "mock_content": "Independent Re-measurement: SQUID magnetometry across 4 independent labs confirms ferromagnetic impurities and copper sulfide phase transitions, with finite resistance > 10^-3 ohm-cm. Zero superconductivity detected.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "REJECTED",
        "supporting_facts": [],
        "contradictions": ["Independent magnetometry revealed finite resistance; samples failed superconductivity tests."],
        "explanation": "Independent physical replication tests refute the claim of zero electrical resistance."
    },
    {
        "scenario": "REJECTED_CLAIM",
        "title": "Zero-Day Remote Code Execution Vulnerability in OpenSSH 9.8",
        "description": "Anonymous security forum disclosure claimed an unauthenticated remote root shell vulnerability in default OpenSSH 9.8 server installations.",
        "criteria": "Official OpenBSD/OpenSSH security advisory or CVE confirmation of reproducible remote root execution.",
        "evidence": [
            {
                "source_url": "https://www.openssh.com/security-bulletin-98-audit",
                "mock_content": "OpenSSH Security Bulletin: The circulating exploit script relies on invalid protocol headers resulting in immediate socket termination. No code execution is possible; claim is a hoax.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "REJECTED",
        "supporting_facts": [],
        "contradictions": ["Vendor security bulletin proves script results in immediate socket termination without execution."],
        "explanation": "Maintainer security bulletin confirms alleged exploit is non-functional."
    },
    {
        "scenario": "REJECTED_CLAIM",
        "title": "LabX Autonomous Artificial General Intelligence Milestone",
        "description": "LabX claimed their synthetic biology agent achieved autonomous general intelligence passing all human benchmarks without prompting.",
        "criteria": "Independent peer-reviewed verification or consensus confirmation of autonomous general intelligence without human intervention.",
        "evidence": [
            {
                "source_url": "https://audit.ai-standards.org/evaluations/labx-debunk",
                "mock_content": "Official Audit: The LabX submission contained prompt leakage and pre-programmed test outputs. The claim of autonomous general intelligence is formally refuted.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "REJECTED",
        "supporting_facts": [],
        "contradictions": ["Audit discovered pre-programmed test outputs and prompt leakage."],
        "explanation": "Independent audit report demonstrates manipulated evaluation data."
    },
    {
        "scenario": "REJECTED_CLAIM",
        "title": "DeFi Protocol Full Solvency and 100% Reserve Collateralization",
        "description": "YieldLend announced its algorithmic stablecoin maintained 100% verifiable liquid collateral backing across on-chain treasuries.",
        "criteria": "Independent crypto auditing firm reserve report and on-chain asset verification matching circulating liability.",
        "evidence": [
            {
                "source_url": "https://certik.com/reports/yieldlend-reserve-forensic",
                "mock_content": "CertiK Forensic Audit: On-chain reserve analysis reveals an unbacked deficit of $78M. Circulating tokens exceed verified reserves by 42%. Solvency claim is false.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "REJECTED",
        "supporting_facts": [],
        "contradictions": ["Auditor identified $78M reserve shortfall with circulating tokens exceeding collateral."],
        "explanation": "On-chain forensic audit disproves 100% reserve backing."
    },
    {
        "scenario": "REJECTED_CLAIM",
        "title": "Commercial Supersonic Overland Flight FAA Exemption Approval",
        "description": "Aviation startup Aerofast asserted the FAA granted commercial airworthiness exemption for Mach 1.6 overland passenger flights.",
        "criteria": "Federal Aviation Administration official docket regulatory exemption order published in the Federal Register.",
        "evidence": [
            {
                "source_url": "https://www.faa.gov/regulations/dockets/aerofast-overland-ruling",
                "mock_content": "FAA Docket Order #2026-441: The petition for exemption from 14 CFR 91.817 (overland supersonic flight ban) is DENIED due to unmitigated sonic boom decibel impact.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "REJECTED",
        "supporting_facts": [],
        "contradictions": ["FAA officially denied the exemption under Docket #2026-441."],
        "explanation": "Regulatory docket confirms formal denial of supersonic overland permit."
    },
    {
        "scenario": "REJECTED_CLAIM",
        "title": "Global Conglomerate Carbon Neutral Net-Zero FY2025 Audit",
        "description": "Apex Mining Group declared their corporate operations achieved net-zero carbon footprint in FY2025 verified by international auditors.",
        "criteria": "Accredited greenhouse gas verification statement confirming Scope 1, 2, and 3 carbon neutralization.",
        "evidence": [
            {
                "source_url": "https://carbonmarketwatch.org/investigations/apex-mining-audit",
                "mock_content": "Investigation Findings: Over 82% of purchased offset credits originated from expired forestry reserves with zero additionality. Net-zero declaration is fundamentally fraudulent.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "REJECTED",
        "supporting_facts": [],
        "contradictions": ["82% of offsets lacked additionality; emissions neutralization claim refuted."],
        "explanation": "Investigative carbon audit proves offset credits were invalid."
    },
    {
        "scenario": "REJECTED_CLAIM",
        "title": "Perpetual Kinetic Energy Harvester Over-Unity Efficiency",
        "description": "EnergyTech patent claimed an over-unity electromagnetic kinetic generator producing 140% output power relative to input excitation.",
        "criteria": "National Renewable Energy Laboratory (NREL) calibrated dynamometer test report validating thermodynamic COP > 1.0.",
        "evidence": [
            {
                "source_url": "https://www.nrel.gov/docs/energytech-dynamometer-eval",
                "mock_content": "NREL Technical Evaluation: Calibrated dynamometer measurements show a coefficient of performance of 0.72. The device operates at a 28% net thermodynamic energy loss.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "REJECTED",
        "supporting_facts": [],
        "contradictions": ["NREL laboratory test measured COP of 0.72, refuting over-unity output."],
        "explanation": "National laboratory physics evaluation confirms thermodynamic deficit."
    },
    {
        "scenario": "REJECTED_CLAIM",
        "title": "Saliva Biomarker 99% Sensitivity Early Cancer Detection Test",
        "description": "OncoSaliva marketed a non-invasive saliva screen claiming 99.4% clinical sensitivity in identifying Stage-1 colorectal carcinomas.",
        "criteria": "FDA 510(k) premarket notification or multi-center clinical validation meeting >=95% sensitivity threshold.",
        "evidence": [
            {
                "source_url": "https://www.fda.gov/inspections-compliance/warning-letters/oncosaliva-letter",
                "mock_content": "FDA Warning Letter: Multi-center blind trial data demonstrates clinical sensitivity of only 31.8% with an unacceptable 44% false positive rate. Marketing claims are deceptive.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "REJECTED",
        "supporting_facts": [],
        "contradictions": ["FDA trial data showed sensitivity of only 31.8% vs 99.4% claimed."],
        "explanation": "FDA regulatory warning letter and clinical trial statistics invalidate the claim."
    },
    {
        "scenario": "REJECTED_CLAIM",
        "title": "Quantum Computer Factorization of RSA-2048 Bit Encryption",
        "description": "Startup QuantumCipher announced their 1,000-qubit processor factored an RSA-2048 public key in under five minutes.",
        "criteria": "Cryptographic public key challenge solution verified by NIST or independent academic peer review.",
        "evidence": [
            {
                "source_url": "https://quantum-computing.report/peer-review/quantumcipher-refutation",
                "mock_content": "Peer Review: Physical analysis of processor noise levels reveals gate fidelity of 96.2%, which is insufficient for Shor's algorithm beyond 15-bit integers. Claim is fabricated.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "REJECTED",
        "supporting_facts": [],
        "contradictions": ["Gate fidelity inadequate for quantum factorization of 2048-bit keys."],
        "explanation": "Peer review analysis proves hardware is physically incapable of factoring target key."
    },

    # =========================================================================
    # 3 INCONCLUSIVE CLAIMS
    # =========================================================================
    {
        "scenario": "INCONCLUSIVE_CLAIM",
        "title": "Undisclosed Acquisition of QuantumBio by Major Pharma",
        "description": "Market rumors alleged an undisclosed definitive agreement for the acquisition of QuantumBio for $500 million cash.",
        "criteria": "Official SEC Form 8-K regulatory filing or joint corporate press release confirming acquisition agreement.",
        "evidence": [
            {
                "source_url": "https://anonymous-rumors.finance-blog.example/quantumbio-sale",
                "mock_content": "[Source Unreachable: HTTP 503 Server Unavailable - DNS resolution failed]",
                "source_version": "0.1"
            }
        ],
        "expected_verdict": "INCONCLUSIVE",
        "supporting_facts": [],
        "contradictions": ["No registered regulatory filings; primary rumor source is offline."],
        "explanation": "Sources were unreachable and no regulatory 8-K filing exists to confirm transaction."
    },
    {
        "scenario": "INCONCLUSIVE_CLAIM",
        "title": "James Webb Telescope Detection of Biogenic Methane on K2-18b",
        "description": "Science blog reported JWST spectroscopic observations definitively confirmed presence of biological-origin dimethyl sulfide on exoplanet K2-18b.",
        "criteria": "NASA Space Telescope Science Institute peer-reviewed data release confirming statistical confidence >= 5-sigma.",
        "evidence": [
            {
                "source_url": "https://stsci.edu/jwst/science-advisories/k2-18b-preliminary",
                "mock_content": "STScI Science Advisory: Preliminary atmospheric transmission spectra show overlapping trace features at 2.4-sigma confidence. Data remains statistically inconclusive pending Cycle 4 observations.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "INCONCLUSIVE",
        "supporting_facts": [],
        "contradictions": ["Detection confidence is only 2.4-sigma, well below required 5-sigma discovery threshold."],
        "explanation": "Observational data lacks required statistical significance to substantiate claim."
    },
    {
        "scenario": "INCONCLUSIVE_CLAIM",
        "title": "Archaeological Seal Inscription Exact 1200 BCE Chronology",
        "description": "Epigraphic society asserted newly discovered Levantine cylinder seal dates precisely to 1200 BCE based on carbon strata.",
        "criteria": "Accelerator mass spectrometry (AMS) radiocarbon dating with standard deviation <= 25 years.",
        "evidence": [
            {
                "source_url": "https://radiocarbon.oxford.edu/reports/levant-seal-ox2026",
                "mock_content": "Oxford Radiocarbon Lab: Strata charcoal yielded calibrated date range 1410 - 1050 BCE (95.4% probability). Inherent calibration plateau precludes narrowing date to single decade.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "INCONCLUSIVE",
        "supporting_facts": [],
        "contradictions": ["Dating confidence range spans 360 years; exact 1200 BCE date cannot be confirmed."],
        "explanation": "Scientific carbon dating confidence interval is too wide to confirm specific year."
    },

    # =========================================================================
    # 3 DISPUTED CLAIMS
    # =========================================================================
    {
        "scenario": "DISPUTED_CLAIM",
        "title": "EcoCapture Carbon Removal Geological Storage Permanence",
        "description": "EcoCapture certified 100,000 metric tons of permanent geological carbon removal in Q3 2026 at Site Alpha.",
        "criteria": "Third-party MRV (Monitoring, Reporting, and Verification) audit certificate with direct sensor telemetry.",
        "evidence": [
            {
                "source_url": "https://mrv-audits.org/reports/ecocapture-q3-2026",
                "mock_content": "Preliminary Certification: Sensor telemetry indicates 100,000 metric tons injected. Awaiting secondary isotope confirmation.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "DISPUTED",
        "supporting_facts": ["Preliminary sensor telemetry confirms injection volume."],
        "contradictions": [],
        "explanation": "Initial verification accepted preliminary sensor data, but dispute challenging permanence is actively open.",
        "dispute": {
            "reason": "Secondary isotope analysis published on November 10 showed injection chamber leak of 15,000 tons, contesting permanent removal claims.",
            "resolution": "Re-evaluation approved with secondary isotope survey evidence attached."
        }
    },
    {
        "scenario": "DISPUTED_CLAIM",
        "title": "Decentralized Lending Oracle Sub-Second Price Feed Accuracy",
        "description": "Oracle network claimed its high-frequency price feed maintained maximum latency under 500ms and deviation under 0.05% during market volatility.",
        "criteria": "On-chain heartbeat timestamp analysis and independent arbitrage telemetry log.",
        "evidence": [
            {
                "source_url": "https://oracle-metrics.org/feed/eth-usd-stress-test",
                "mock_content": "Telemetry Snapshot: 99.8% of heartbeat updates landed within 480ms during volatility stress test.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "DISPUTED",
        "supporting_facts": ["Telemetry log indicates 99.8% heartbeats met latency spec."],
        "contradictions": [],
        "explanation": "Initial performance data approved, but liquidation victims disputed an unrecorded 14-second blackout.",
        "dispute": {
            "reason": "Borrower consortium submitted on-chain transaction traces proving a 14-second stale oracle heartbeat during block 20491823 triggered $420k unwarranted liquidations.",
            "resolution": "Dispute lodged under validator arbitration review."
        }
    },
    {
        "scenario": "DISPUTED_CLAIM",
        "title": "Phase II Oncology Trial Progression-Free Survival Rate",
        "description": "Biotech firm announced 88% progression-free survival endpoint met in Phase II non-small cell lung carcinoma clinical trial.",
        "criteria": "Independent Data Monitoring Committee (IDMC) validated statistical analysis plan and unblinded cohort report.",
        "evidence": [
            {
                "source_url": "https://clinicaltrials.gov/study/NCT06294012/preliminary-pfs",
                "mock_content": "Sponsor Preliminary Summary: 44 of 50 patients demonstrated progression-free survival at month 12.",
                "source_version": "1.0"
            }
        ],
        "expected_verdict": "DISPUTED",
        "supporting_facts": ["Sponsor summary shows 44 of 50 patients reached month 12 PFS."],
        "contradictions": [],
        "explanation": "Sponsor interim filing accepted, but institutional monitoring committee challenged cohort selection bias.",
        "dispute": {
            "reason": "Data Monitoring Committee notified regulators of improper exclusion of 12 drop-out patients from the evaluable denominator, artificially inflating survival percentage.",
            "resolution": "Formal audit initiated; claim remains in DISPUTED state."
        }
    }
]

# Compute real SHA-256 hashes for all evidence mock_contents
for c in claims:
    for ev in c.get("evidence", []):
        if "content_hash" not in ev:
            ev["content_hash"] = h(ev["mock_content"])

target_path = Path(__file__).resolve().parent.parent / "examples" / "sample_claims.json"
with open(target_path, "w", encoding="utf-8") as f:
    json.dump(claims, f, indent=2)

print(f"Successfully wrote {len(claims)} sample claims to {target_path}")

# Count breakdown
ver = sum(1 for c in claims if c["expected_verdict"] == "VERIFIED")
rej = sum(1 for c in claims if c["expected_verdict"] == "REJECTED")
inc = sum(1 for c in claims if c["expected_verdict"] == "INCONCLUSIVE")
dis = sum(1 for c in claims if c["expected_verdict"] == "DISPUTED")
print(f"Summary: Verified={ver}, Rejected={rej}, Inconclusive={inc}, Disputed={dis}")
print(f"Disputed + Inconclusive total = {dis + inc}")
print(f"Total claims = {len(claims)}")
