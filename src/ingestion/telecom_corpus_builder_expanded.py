"""
telecom_corpus_builder_expanded.py

Generates ADDITIONAL passages extracted from official Indian operator Telecom
Consumer Charters (Jio, Airtel, Vi/Vodafone Idea) sourced from the merged PDF.

These passages are APPENDED to the existing passages.jsonl produced by
telecom_corpus_builder.py. They do NOT replace the original passages.

Source documents (merged PDF):
    - Reliance Jio Infocomm Limited — Telecom Consumer Charter
    - Bharti Airtel Limited — Telecom Consumer Charter (Mobile and Fixed Line)
    - Vodafone Idea Limited (Vi) — Telecom Consumer Charter

Output:
    data/raw/telecom_kb/passages.jsonl   ← appended with new passages

Each passage uses the EXACT schema from telecom_corpus_builder.py:
    {
        "id":         "tc_XXXX",
        "title":      "...",
        "text":       "...",
        "category":   "...",
        "domain":     "telecom",
        "source":     "charter_pdf_v1",
        "char_count": int
    }

Usage:
    python telecom_corpus_builder_expanded.py
    python telecom_corpus_builder_expanded.py --output_dir data/raw/telecom_kb --start_id 400
"""

import json
import argparse
from pathlib import Path



# ─────────────────────────────────────────────────────────────────────────────
#  JIO CHARTER PASSAGES
# ─────────────────────────────────────────────────────────────────────────────
JIO_PASSAGES = [
    # ── Tariffs & Plan Information ────────────────────────────────────────────
    {
        "title": "Jio — How to Check Your Current Tariff Plan",
        "text": (
            "To know your current tariff information on Jio, you may dial 199 from your "
            "Jio number. You can also SMS MY PLAN to 199, log on to www.Jio.com, or "
            "download the MyJio App from Google Playstore (Android) or Apple Store "
            "(iPhone). A tariff plan once offered shall be available to a subscriber for "
            "a minimum period of 6 months from the date of enrollment. You are free to "
            "choose any other tariff plan even during the 6-month period. For postpaid "
            "plans, all plan change requests are accepted and implemented from the next "
            "billing cycle and confirmed to you at the time of placing the request."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Jio — 30-Day Advance Notice Before Plan Termination",
        "text": (
            "Jio is required to give an advance notice of not less than 30 days to TRAI "
            "and to subscribers before terminating an existing tariff plan. This means "
            "if Jio decides to discontinue any plan you are enrolled on, you will receive "
            "at least 30 days notice. You are also free to migrate to any other available "
            "plan during this period without any migration fee."
        ),
        "category": "billing_recharge",
    },
    # ── Jio MNP ──────────────────────────────────────────────────────────────
    {
        "title": "Jio — Mobile Number Portability (MNP) — How to Port Out",
        "text": (
            "To port your number out of Jio: You must approach the recipient operator "
            "(the operator you want to port to). You may be required to pay a porting "
            "charge of up to Rs.6.46 to the recipient operator. To obtain the Unique "
            "Porting Code (UPC), SMS PORT followed by your 10-digit mobile number to "
            "1900. You will receive an auto-generated 8-digit UPC. The UPC is valid for "
            "4 days for all LSAs except Jammu & Kashmir, North East, and Assam, where "
            "it is valid for 30 days. Eligibility: 90 days must have elapsed since "
            "activation or last porting. No outstanding payments must be due."
        ),
        "category": "sim_esim",
    },
    {
        "title": "Jio — MNP UPC Rejection — Grounds",
        "text": (
            "Your request for a UPC (Unique Porting Code) to port out of Jio can be "
            "denied on the following grounds: outstanding payments due by way of pending "
            "bills; porting request made before the expiry of 90 days from activation "
            "or previous porting; request made before 7 days of SIM swap or replacement; "
            "a change-of-ownership request is under process; the mobile number is "
            "sub-judice; porting has been prohibited by a Court of Law; subsisting "
            "contractual obligations not complied with; or a porting request is already "
            "in process for the same number. You will be informed of the reason for "
            "UPC non-issuance."
        ),
        "category": "sim_esim",
    },
    {
        "title": "Jio — MNP — No Service Period and Request Withdrawal",
        "text": (
            "When porting your number from Jio to another operator, you may experience "
            "a 'no service' period for up to 2 hours during the actual porting. You may "
            "withdraw your porting request within 24 hours of its submission to the "
            "recipient operator. After porting is complete, you will need to insert the "
            "new SIM provided by the recipient operator to access their service. For "
            "prepaid customers, any remaining talktime balance and entitlements at the "
            "time of porting will lapse and will not be transferred."
        ),
        "category": "sim_esim",
    },
    # ── Jio VAS ───────────────────────────────────────────────────────────────
    {
        "title": "Jio — Value Added Services (VAS) — Consent and Deactivation",
        "text": (
            "No Value Added Service (VAS) shall be provided to you by Jio without your "
            "explicit consent. If any VAS is provided free as part of a trial or free "
            "look period, it shall not be charged post the free look period without your "
            "explicit consent. Three days before the renewal of a subscribed VAS, you "
            "will receive an SMS confirming the renewal date, charges, and a toll-free "
            "number to unsubscribe. To unsubscribe from any VAS: dial 155223 (toll free) "
            "or send STOP to 155223. You will receive a list of all active VAS and can "
            "deactivate by confirming your choice."
        ),
        "category": "billing_recharge",
    },
    # ── Jio DND / TCCPR ──────────────────────────────────────────────────────
    {
        "title": "Jio — DND and TCCPR — Stopping Unwanted Commercial Communications",
        "text": (
            "To stop receiving commercial communications (calls/SMS) on Jio, dial or "
            "SMS 1909 (toll free) and register under one of two categories: "
            "Fully Blocked — stops all commercial calls/SMS; "
            "Partially Blocked — stops all commercial communications except SMS from "
            "one selected preference category. "
            "The 8 preference categories are: Banking/Insurance/Financial/Credit Cards "
            "(1), Real Estate (2), Education (3), Health (4), Consumer goods and "
            "automobiles (5), Communication/Broadcasting/Entertainment/IT (6), Tourism "
            "& Leisure (7), Food & Beverages (8). "
            "Example: to block Health SMS only, send STOP 4 to 1909. "
            "No telemarketing calls/SMS are permitted between 9:00 PM and 10:00 AM. "
            "To report UCC, email 1909@Jio.com or use the MyJio app."
        ),
        "category": "ivr_complaints",
    },
    # ── Jio Complaint Redressal ───────────────────────────────────────────────
    {
        "title": "Jio — Customer Care Contact Numbers and Channels",
        "text": (
            "Jio customer care is available 24 hours a day, 365 days a year. "
            "To reach Jio Care: "
            "Call 198 (toll free, complaints) or 199 (toll free, general information) "
            "from your Jio number. "
            "Call 1800-88-99999 (Jio Mobile) or 1800-896-9999 (Jio Fiber) from any number. "
            "Email: care@jio.com. "
            "Log complaints/queries on the MyJio app. "
            "WhatsApp: 70007 70007 (Jio Mobile) or 70005 70005 (Jio Fiber). "
            "Visit the nearest Jio store. "
            "Contact Jio on social media. "
            "Always note the unique docket number provided when registering a complaint "
            "— you will need it for all future communications."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "Jio — Complaint Redressal — Two-Level Mechanism",
        "text": (
            "Jio operates a two-level grievance redressal mechanism as per TRAI's "
            "Telecom Consumers Complaint Redressal Regulations, 2012: "
            "Level 1 — Contact Center: Register via 198, 199, 1800-88-99999, "
            "care@jio.com, MyJio app, WhatsApp, or Jio store. A unique docket number "
            "is issued for every complaint. Resolution time is as per TRAI regulations "
            "and is confirmed at the time of registration. "
            "Level 2 — Appellate Authority: If unsatisfied with Level 1 resolution, "
            "appeal to the Appellate Authority by phone (18008893999), fax, post, email, "
            "or in person. The appeal must be filed within 30 days after expiry of the "
            "complaint resolution time limit (extensions up to 3 months may be considered). "
            "The appeal is decided within 39 days of filing."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "Jio — Appellate Authority — Process and Timeline",
        "text": (
            "The Jio Appellate Authority handles second-level grievances for unresolved "
            "complaints. Contact: phone 18008893999, fax 18008891211, or email to the "
            "regional appellate address (e.g. appellate.del@jio.com for Delhi, "
            "appellate.mum@jio.com for Mumbai, appellate.guj@jio.com for Gujarat). "
            "Working hours: Monday to Friday, 10:30 AM to 6:00 PM. "
            "Key timelines: docket number communicated within 3 days of filing; "
            "appeal decided within 39 days. "
            "Provide your original complaint docket number when appealing — this gives "
            "the Appellate Authority access to your full case history."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "Jio — Web-Based Complaint Monitoring System",
        "text": (
            "To check the status of a Jio complaint or log a new complaint online, "
            "visit www.jio.com or open the MyJio App. Log in with your Jio ID and "
            "password and navigate to 'Service Requests' under your profile tab. "
            "A unique Service Request number is provided for every complaint registered. "
            "You can track resolution status in real time through this portal. "
            "The same portal can be used to submit feedback on whether your complaint "
            "was satisfactorily resolved."
        ),
        "category": "ivr_complaints",
    },
    # ── Jio QoS ───────────────────────────────────────────────────────────────
    {
        "title": "Jio — TRAI Quality of Service Benchmarks — Network Availability",
        "text": (
            "TRAI-prescribed QoS benchmarks for Jio wireless services — Network Availability: "
            "Geospatial coverage map availability on website: ≥99% working cells. "
            "Cumulative cell downtime: ≤1.5%. "
            "Worst affected cells due to downtime: ≤1.5%. "
            "Significant network outage (district-level outage >4 hours) must be reported "
            "to TRAI within 24 hours. "
            "Compensation for outages lasting more than 24 hours: "
            "Postpaid subscribers — proportional rent rebate (plan charge / days) "
            "credited in the next bill. "
            "Prepaid subscribers — validity of subscribed tariff extended by the "
            "number of affected days."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "Jio — TRAI QoS Benchmarks — Voice and Data",
        "text": (
            "TRAI-prescribed QoS benchmarks for Jio wireless services — Voice and Data: "
            "Call Set-up Success Rate (intra-network): ≥98%. "
            "Call Set-up Success Rate (inter-network, incoming): ≥95%. "
            "POI Congestion: ≤0.5% (90th percentile). "
            "Dropped Call Rate (4G/5G Packet Switched): ≤2%. "
            "Downlink and Uplink Packet Drop Rate (4G/5G): ≤2% each. "
            "Latency (4G and 5G): ≤75ms. "
            "Packet Drop Rate (4G/5G broadband): ≤3%. "
            "Download/upload speed ≥ advertised: 80th percentile of test samples. "
            "Jitter (4G/5G): ≤50ms. "
            "Connections with good voice quality: ≥95%. "
            "SMS delivery success (intra-network): ≥95%."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "Jio — TRAI QoS Benchmarks — Customer Service",
        "text": (
            "TRAI-prescribed customer service benchmarks for Jio: "
            "Billing and charging complaints: ≤0.1% of subscriber base. "
            "Resolution of billing/charging complaints: 100% within 4 weeks. "
            "Application of adjustment to customer account: 100% within 1 week of "
            "complaint resolution or fault rectification. "
            "Call centre accessibility: ≥95%. "
            "Calls answered by operator (voice-to-voice) within 90 seconds: ≥95%. "
            "Termination/closure of service within 7 working days of request: 100%. "
            "Refund of deposits within 45 days of closure or non-provisioning: 100%. "
            "These benchmarks apply to both wireless and wireline services."
        ),
        "category": "ivr_complaints",
    },
    # ── Jio Disconnection / Service Termination ───────────────────────────────
    {
        "title": "Jio — How to Terminate / Disconnect Your Service",
        "text": (
            "To terminate your Jio service: Contact Jio through customer care (198/199), "
            "send a written request, email care@jio.com, or visit the nearest Jio store. "
            "Services will be disconnected within 7 working days of your request. "
            "Termination is subject to the return or recovery of any CPE equipment "
            "provided by Jio, where applicable. Any refund due after adjusting "
            "outstanding dues will be processed within 60 days of termination. "
            "For JioFiber: one-time charges (activation, installation) are forfeited "
            "on exit. After service is availed, plan charges are also forfeited."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Jio — Prepaid Disconnection — 90-Day Non-Usage Policy",
        "text": (
            "For Jio prepaid connections: service will be discontinued if there is no "
            "usage — no voice/video calls (outgoing or incoming), no outgoing SMS, no "
            "data session, no VAS purchases — for a continuous period of 90 days. "
            "Subscribers with less than Rs.20 balance: all services are deactivated and "
            "a reactivation fee applies for 15 days, after which the number is "
            "disconnected on non-payment. "
            "Subscribers with Rs.20 or more balance: Automatic Number Retention Scheme "
            "(ANRS) deducts Rs.20 and extends services by 30 days. This continues until "
            "balance falls below Rs.20, after which the above process applies."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Jio Postpaid — Safe Custody Option",
        "text": (
            "Jio postpaid customers who are unable to use services temporarily can opt "
            "for the Safe Custody facility. By paying Rs.150 for every 3 months or part "
            "thereof, services are placed in safe custody and the number is not "
            "disconnected for non-usage. To activate or know more about Safe Custody, "
            "call 199 or visit www.jio.com. Without this facility, postpaid connections "
            "without any usage (voice, video, SMS, data, VAS) for 90 days are liable "
            "for deactivation at Jio's discretion."
        ),
        "category": "billing_recharge",
    },
    # ── Jio Billing ───────────────────────────────────────────────────────────
    {
        "title": "Jio Postpaid — Billing, Payment, and Late Fees",
        "text": (
            "Jio bills postpaid customers on a fixed billing cycle. Bills include all "
            "applicable taxes and cess. Bill or notices are sent to the billing address "
            "registered on the account. All payments must be made by the due date stated "
            "in the billing statement. "
            "Payments beyond the due date attract late fees as prescribed by Jio. "
            "If there is any dispute regarding charges, the customer must intimate "
            "Jio in writing within 7 days of receiving the bill. Full disputed charges "
            "must still be paid while the dispute is pending. "
            "Upon delayed or non-payment, Jio may suspend services partially or fully. "
            "Security deposit, if any, will be adjusted against dues and the balance "
            "refunded within 60 days of service deactivation."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Jio — Itemized Bill on Request",
        "text": (
            "Jio postpaid customers can request an itemized usage bill showing all call "
            "data records, including voice calls, SMS, data sessions, VAS, roaming, and "
            "premium rate services, along with their monetary values. This is provided "
            "at a reasonable cost in accordance with TRAI regulations. To request an "
            "itemized CDR (Call Detail Record), contact Jio customer care at 199 or "
            "through the MyJio app. The CDR is useful when disputing specific charges "
            "on your bill."
        ),
        "category": "billing_recharge",
    },
    # ── Jio Roaming ───────────────────────────────────────────────────────────
    {
        "title": "Jio — National Roaming Policy",
        "text": (
            "When roaming outside your Jio home service area within India, applicable "
            "operator-specific tariffs will be charged for voice, SMS, and data. Roaming "
            "charges are subject to the ceiling prescribed by TRAI. All VAS that you "
            "have subscribed to with Jio are available while roaming, provided the "
            "visited network supports them. Applicable tariffs of the visited operator "
            "will apply to VAS used while roaming. Jio supports nationwide roaming as "
            "part of its pan-India network license."
        ),
        "category": "roaming_international",
    },
    {
        "title": "Jio — International Roaming — Key Customer Obligations",
        "text": (
            "When using Jio international roaming services: "
            "You must ensure that your handset/device is compatible with the frequency "
            "bands used by the visited network. Jio is not responsible if you cannot "
            "avail roaming services due to device incompatibility. "
            "Charges while roaming internationally will differ from home network rates "
            "and vary by destination operator. "
            "For international roaming, an additional security deposit or fee may be "
            "required. "
            "You are advised to check Jio's international roaming pack rates at "
            "www.jio.com or the MyJio app before travel."
        ),
        "category": "roaming_international",
    },
    # ── Jio SIM / Device ──────────────────────────────────────────────────────
    {
        "title": "Jio — SIM Card — Ownership and Replacement",
        "text": (
            "The SIM card provided by Jio is and shall always remain the sole and "
            "absolute property of Reliance Jio Infocomm Limited (RJIL), even after "
            "termination of services. If your SIM is lost or stolen, report to the "
            "Police and then call Jio customer care (198) to request deactivation. "
            "Until the SIM is deactivated, you are liable for all charges incurred. "
            "Jio will replace the SIM card as soon as reasonably practicable upon "
            "receiving your request, subject to applicable replacement charges and "
            "submission of an FIR copy."
        ),
        "category": "sim_esim",
    },
    {
        "title": "Jio — IMEI Code and Device Compliance",
        "text": (
            "Customers using Jio services must always use equipment with a valid IMEI "
            "(International Mobile Equipment Identity) code. If your device's IMEI code "
            "is not traceable or valid on the Jio network, Jio reserves the right to "
            "disconnect services without prior notice, as per government requirements. "
            "Customers must ensure their device is compatible with the frequency bands "
            "allotted to Jio in their service area. Jio is not liable for any issues "
            "arising from device-network incompatibility."
        ),
        "category": "sim_esim",
    },
    {
        "title": "Jio — KYC Documents Accepted for New Connection",
        "text": (
            "Valid KYC documents for a Jio new connection include: "
            "Proof of Identity (with photo): Aadhaar (UIDAI), Passport, Driving License, "
            "Election Commission ID, Arms License, PAN Card, Photo Credit Card, "
            "CGHS/ECHS card, Pensioner/Freedom Fighter/Kissan card with photo, "
            "Government/PSU photo ID card, or Caste/Domicile Certificate with photo. "
            "Proof of Address: Aadhaar, Passport, Driving License, Election ID, "
            "Water/Telephone/Electricity bill (not older than 3 months), "
            "IT Assessment Order (not older than 1 year), Vehicle RC, Registered "
            "Sale/Lease Agreement, or Bank passbook. "
            "Aadhaar OTP-based eKYC is the fastest method and can be done digitally."
        ),
        "category": "sim_esim",
    },
    # ── JioFiber ──────────────────────────────────────────────────────────────
    {
        "title": "JioFiber — Fair Usage Policy (FUP) and Contention Ratio",
        "text": (
            "JioFiber and JioAirFiber services operate under a Fair Usage Limit (FUL) "
            "and/or Commercial Usage Policy (CUP) on certain high-speed internet plans. "
            "All advertised speeds are guaranteed up to the ISP (Internet Service Provider) "
            "node. TRAI's prescribed contention ratio applies to all JioFiber plans and "
            "is subject to change as per TRAI directives. "
            "The FUP/CUP policy is published at www.jio.com and updated regularly. "
            "Customers are encouraged to check the FUP regularly. "
            "Any Wi-Fi connectivity set up by the subscriber on the JioFiber network "
            "must be registered for centralized authentication (per DoT Wi-Fi directive)."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "JioFiber — CPE Return and Penalty on Exit",
        "text": (
            "Jio may provide Customer Premise Equipment (CPE) such as modems, routers, "
            "batteries, and accessories for JioFiber and JioAirFiber services. "
            "The CPE must be returned to Jio upon termination of services or when "
            "requested by Jio. An interest-free security deposit may be collected at "
            "the time of CPE issue. "
            "If CPE is not returned or is returned in damaged/non-working condition, "
            "penalty charges apply and may be deducted from the security deposit. "
            "The customer must not move, modify, or transfer the CPE. Any account "
            "refund upon exit is processed within 8 weeks after receipt of Jio-owned "
            "equipment and settlement of all outstanding charges."
        ),
        "category": "billing_recharge",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
#  AIRTEL CHARTER PASSAGES
# ─────────────────────────────────────────────────────────────────────────────
AIRTEL_PASSAGES = [
    # ── Airtel Prepaid T&C ────────────────────────────────────────────────────
    {
        "title": "Airtel — Prepaid SIM Activation and Verification",
        "text": (
            "For an Airtel prepaid SIM, the first outgoing call is redirected to the "
            "Call Center for telephonic verification. Activation is subject to positive "
            "telephonic verification. If the connection is not positively verified, "
            "no refunds will be processed and the submitted documents remain with "
            "Airtel. Activation of the new SIM must be concluded within 30 days of "
            "signing the CAF (Customer Application Form). If not completed in 30 days, "
            "Airtel may reject the connection and cancel the number without refund. "
            "Airtel also reserves the right to physically verify the customer's address."
        ),
        "category": "sim_esim",
    },
    {
        "title": "Airtel — Prepaid Non-Usage Disconnection Policy",
        "text": (
            "Airtel prepaid SIM service will be discontinued if there is no usage "
            "(no voice calls, outgoing SMS, data usage, or VAS) for a continuous period "
            "of 90 days. No refunds will be given for unused talktime balance or "
            "validity remaining on the card. If the main account balance is less than "
            "Rs.20 upon deactivation, a grace period of 15 days is provided — the "
            "subscriber can retain the number by paying Rs.20 within this period. "
            "If the balance is Rs.20 or more, a number retention charge of Rs.20 is "
            "automatically deducted every 30 days, extending the non-usage period."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Airtel — SIM Card Ownership and Number Rights",
        "text": (
            "The SIM card issued by Airtel is and shall always remain the sole property "
            "of Bharti Airtel Limited. The mobile number assigned to you is and shall "
            "always remain in the sole and exclusive domain of Bharti Airtel Limited. "
            "You cannot transfer, assign, or lease the SIM card or mobile number to "
            "any other person under any circumstances. Upon expiry or deactivation of "
            "your connection, Airtel may re-allocate your number to another customer "
            "in accordance with TRAI regulations. You have no lien or right over the "
            "mobile number at any point of time."
        ),
        "category": "sim_esim",
    },
    {
        "title": "Airtel — Prepaid Tariff Plan — Validity and Grace Period",
        "text": (
            "Airtel prepaid recharge coupons/balances are non-refundable and "
            "non-transferable. Airtel reserves the right to change the validity of "
            "unsold recharge cards at any time without prior notice, subject to TRAI "
            "regulations. Airtel may also change the composition of recharge coupons, "
            "their validity period, or grace periods in accordance with applicable TRAI "
            "regulations. No increase is permissible in any item of the tariff for a "
            "period of 6 months from the date of enrollment under a tariff plan, as "
            "per TRAI guidelines."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Airtel — Data Services Activation — Explicit Consent Required",
        "text": (
            "In line with TRAI regulations, Airtel customers who have not availed any "
            "data pack will be provided data facility only after giving explicit consent "
            "on toll-free number 1925 through SMS or IVR. To start data services, "
            "send SMS 'Start' to 1925. To deactivate data services, send SMS 'Stop' "
            "to 1925. This consent requirement prevents unexpected data charges for "
            "customers who do not wish to use mobile data without an active data plan. "
            "Existing data pack customers are not affected by this requirement."
        ),
        "category": "connectivity_5g",
    },
    # ── Airtel Postpaid Billing ────────────────────────────────────────────────
    {
        "title": "Airtel — Postpaid Late Payment Charges",
        "text": (
            "Airtel postpaid customers must pay their bill by the due date to ensure "
            "uninterrupted services and avoid late payment charges. "
            "Late payment charges applicable on non-payment of bill on or before the "
            "due date: Rs.100 or 2% of invoice value, whichever is higher, subject to "
            "a maximum of Rs.300. "
            "Paying on time also helps maintain a good credit limit. The credit limit "
            "is set at Airtel's sole discretion and is an indicator of monthly usage — "
            "if usage exceeds the credit limit, the customer is liable for all charges "
            "even beyond the stated limit."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Airtel — Security Deposit Refund on Disconnection",
        "text": (
            "Upon permanent disconnection of an Airtel postpaid service, the security "
            "deposit will be refunded to the customer within 60 days of disconnection. "
            "Any delay beyond 60 days in refunding the deposit attracts interest at "
            "10% per annum on the delayed amount. Bills are raised only after adjustment "
            "of the security deposit. Closure or termination of service will not be "
            "made conditional upon payment of dues or settlement of disputes. "
            "No fixed monthly charges such as rental will be charged beyond 7 days "
            "from the date of the termination request or from the date of last usage, "
            "whichever is later."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Airtel — Itemized Usage Bill on Request",
        "text": (
            "Airtel customers can request an itemized usage bill that shows actual "
            "service usage details, including all call data records, value added "
            "services, premium rate services, and roaming charges, along with their "
            "monetary values. This is provided at a reasonable cost in accordance with "
            "TRAI regulations. To request an itemized CDR, contact Airtel customer "
            "care at 121 or visit an Airtel Relationship Center."
        ),
        "category": "billing_recharge",
    },
    # ── Airtel Service Suspension / Disconnection ─────────────────────────────
    {
        "title": "Airtel — Grounds for Service Suspension or Disconnection",
        "text": (
            "Airtel reserves the right to suspend or disconnect services for any of "
            "the following reasons: Government/TRAI orders or directions; technical "
            "failure, maintenance, or network upgrades; combat potential fraud or "
            "sabotage; service used in violation of law; customer fails credit check "
            "or provides incorrect information; non-payment of dues; breach of "
            "Commercial Communication Customer Preference Regulations (telemarketing "
            "without registration); the customer is declared insolvent/bankrupt; "
            "interconnection failure between Airtel and another service provider; "
            "or any other reason found reasonable by Airtel. Force majeure "
            "circumstances (Acts of God) also apply."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Airtel — Individual Connection Limit — 9 Connections Maximum",
        "text": (
            "As per regulatory guidelines, if an individual customer has a total of "
            "9 connections under his or her name across all service providers, no "
            "additional connection will be granted. If it is found that a customer "
            "has more than 9 connections across operators that remained undeclared, "
            "Airtel reserves the right to disconnect the additional connections with "
            "immediate effect and without prior notice. This applies to ensure "
            "compliance with DoT's subscriber verification norms."
        ),
        "category": "sim_esim",
    },
    # ── Airtel MNP ────────────────────────────────────────────────────────────
    {
        "title": "Airtel — MNP Rights — Customer Right to Port Out",
        "text": (
            "As per TRAI's Telecommunication Mobile Number Portability Regulations 2009, "
            "Airtel customers have the right to retain their number while moving to "
            "another mobile service provider. Porting is allowed after 90 days from "
            "the date of activation or last porting, whichever is applicable. "
            "Porting timelines: 2 working days for intra-LSA (within the same telecom "
            "circle) porting; 4 working days for inter-LSA (between different circles). "
            "The UPC validity is 4 days for most circles (except J&K, Assam, North East "
            "where it is unchanged). Port fee is non-refundable if request is cancelled. "
            "Port-in request can be cancelled within 24 hours of submission."
        ),
        "category": "sim_esim",
    },
    # ── Airtel VAS ────────────────────────────────────────────────────────────
    {
        "title": "Airtel — VAS Consumer Rights and Protection",
        "text": (
            "Airtel cannot activate any chargeable VAS (Value Added Service) without "
            "explicit customer consent. Any VAS previously provided free of charge "
            "cannot be made chargeable without explicit consent. No chargeable VAS "
            "can be activated by a single key-press on the handset. "
            "If a subscriber seeks to unsubscribe within 24 hours of accidental VAS "
            "activation, Airtel must unsubscribe and fully reimburse the charge deducted. "
            "Three days before a VAS renewal, Airtel will notify you of the renewal "
            "date, charges, and toll-free unsubscription number. "
            "To stop VAS: SMS STOP to 155223 (toll free) or call 155223."
        ),
        "category": "billing_recharge",
    },
    # ── Airtel DND ────────────────────────────────────────────────────────────
    {
        "title": "Airtel — DND Registration — How to Stop Promotional Calls and SMS",
        "text": (
            "To stop receiving unwanted telemarketing calls and SMS on Airtel: "
            "Call 1909 (toll free) and speak to a customer care executive. "
            "SMS 'START DND' or 'FULLY BLOCK' to 1909 for full blocking. "
            "For partial blocking by category, use 'BLOCK 1' through 'BLOCK 8'. "
            "Register at www.ndnc.net.in. "
            "DND complaints can also be filed via: form at airtel.in/dnd; "
            "email 1909@airtel.com with call/SMS date and sender details; "
            "SMS the promotion details and sender number to 1909. "
            "DND takes 7 days to become effective. "
            "If your number is used for unsolicited promotions, all numbers under "
            "the same name and address will be disconnected and blacklisted for 2 years."
        ),
        "category": "ivr_complaints",
    },
    # ── Airtel Complaint Redressal ─────────────────────────────────────────────
    {
        "title": "Airtel — Customer Care and Complaint Contact Details",
        "text": (
            "Airtel customer care is accessible from anywhere in India, including while "
            "roaming. Key contact details: "
            "General information / queries: dial 121 (0.50p per 3 minutes from Airtel "
            "mobile for agent assistance). "
            "Complaints: dial 198 (toll free from Airtel mobile). "
            "Email: 121@Airtel.com. "
            "Website: www.Airtel.in (click 'Need Help'). "
            "Head Office: Bharti Airtel Ltd, Airtel Center, Plot No.16, Udyog Vihar, "
            "Phase IV, Gurgaon-122015. "
            "Airtel Relationship Centers are present in all cities where Airtel provides "
            "service."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "Airtel — Two-Level Complaint Redressal Process",
        "text": (
            "Airtel provides a two-level complaint redressal mechanism: "
            "Level 1 — Complaint Center: Contact via 121 (queries), 198 (complaints, "
            "toll free), 121@Airtel.com, www.Airtel.in, or an Airtel Relationship Center. "
            "A unique Service Request number is issued for every complaint. You are "
            "informed via SMS of the resolution timeline. If the first resolution is "
            "unsatisfactory, share your dissatisfaction and Airtel will re-assess "
            "within 10 days. "
            "Level 2 — Appellate Authority: If Level 1 does not satisfy you, approach "
            "the Appellate Authority by email (region-specific, see Annexure II). "
            "Working hours: 9:30 AM to 6:30 PM, Monday to Friday. "
            "Unique reference number issued within 3 days. Appeal decided within 39 "
            "working days of filing."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "Airtel — Appellate Authority Email Addresses by Circle",
        "text": (
            "Airtel Appellate Authority email addresses for different telecom circles: "
            "Delhi NCR: appellate.del@in.airtel.com, "
            "Mumbai: appellate.mum@in.airtel.com, "
            "Maharashtra & Goa: appellate.mah@in.airtel.com, "
            "Karnataka: appellate.kk@in.airtel.com, "
            "Tamil Nadu: appellate.tn@in.airtel.com, "
            "Kerala: appellate.ker@in.airtel.com, "
            "Andhra Pradesh: appellate.ap@in.airtel.com, "
            "Kolkata: appellate.wb@in.airtel.com, "
            "Gujarat: appellate.guj@in.airtel.com, "
            "Punjab: appellate.pb@in.airtel.com, "
            "Rajasthan: appellate.raj@in.airtel.com, "
            "Jammu & Kashmir: appellate.jk@in.airtel.com, "
            "Himachal Pradesh: appellate.hp@in.airtel.com, "
            "Bihar & Jharkhand: appellate.bihar@in.airtel.com, "
            "North East: appellate.nesa@in.airtel.com. "
            "Appellate Authority responds within 39 working days of filing."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "Airtel — Termination and Disconnection of Service",
        "text": (
            "Airtel customers can request termination of service by: written request, "
            "fax, email (preferably the registered email), SMS, or telephone call to "
            "the customer care number. Service closure is completed within a maximum "
            "of 7 days uniformly for all request methods. "
            "After the termination request: no rental or other charges shall be levied "
            "beyond 7 days; bills are raised only after adjustment of the security "
            "deposit; closure is not conditional on payment of outstanding dues. "
            "Security deposit refund is made within 60 days. Delays attract interest "
            "at 10% per annum."
        ),
        "category": "billing_recharge",
    },
    # ── Airtel QoS ────────────────────────────────────────────────────────────
    {
        "title": "Airtel — TRAI QoS Benchmarks — Network Outage Compensation",
        "text": (
            "TRAI mandates compensation to Airtel subscribers for significant network "
            "outages (where services are unavailable in a district for more than 4 "
            "hours): "
            "Significant outages must be reported to TRAI within 24 hours. "
            "Compensation for outages exceeding 24 hours: "
            "Postpaid subscribers — proportional rent rebate (plan charges / days "
            "affected) credited in the next bill (100%). "
            "Prepaid subscribers — validity of subscribed plan extended by the number "
            "of affected days (100%). "
            "Cell downtime benchmark: ≤1.5% cumulative. "
            "Worst affected cells: ≤1.5%."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "Airtel — TRAI QoS — Wireline Broadband Benchmarks",
        "text": (
            "TRAI-prescribed benchmarks for Airtel wireline broadband services: "
            "Service provisioning within 7 working days: ≥98%. "
            "Latency: ≤50ms. Packet Drop Rate: ≤1%. "
            "Download/upload speed ≥ offered typical speed: 90th percentile of test samples. "
            "Bandwidth utilization (node to ISP gateway): ≤80%. "
            "Jitter: ≤40ms. "
            "Fault incidences per 100 subscribers: ≤5. "
            "Fault repair by next working day: ≥85%. "
            "Fault repair within 3 working days: ≥99%. "
            "For faults unresolved after 3 working days: postpaid customers receive "
            "proportional rent rebate; prepaid customers receive validity extension."
        ),
        "category": "connectivity_5g",
    },
    # ── Airtel Roaming ────────────────────────────────────────────────────────
    {
        "title": "Airtel — Prepaid Roaming — Pre-activated Facility",
        "text": (
            "Airtel prepaid SIM cards come with a pre-activated roaming facility. "
            "Roaming charges are as decided by Airtel from time to time, subject to "
            "TRAI regulations. When roaming outside the home network, customers must "
            "ensure their handset is compatible with the frequency of the visiting "
            "network. Airtel is not responsible or liable for non-provision of roaming "
            "services due to device incompatibility. Network coverage availability in "
            "any area or at any time is not guaranteed and cannot be a basis for a "
            "claim against Airtel."
        ),
        "category": "roaming_international",
    },
    # ── Airtel SMS Charging ────────────────────────────────────────────────────
    {
        "title": "Airtel — SMS Charging Rules — 160 Character Limit",
        "text": (
            "As per GSM technical standards, a single SMS contains a maximum of 160 "
            "characters of user data (words, numbers, or alphanumeric). Any SMS "
            "containing more than 160 characters is delivered as separate messages and "
            "charged as separate SMS per the applicable tariff. For example, a 320 "
            "character message will be charged as 2 SMS. This applies to both prepaid "
            "and postpaid Airtel connections. The charge is incurred as soon as the "
            "message leaves Airtel's SMS center."
        ),
        "category": "billing_recharge",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
#  VI (VODAFONE IDEA) CHARTER PASSAGES
# ─────────────────────────────────────────────────────────────────────────────
VI_PASSAGES = [
    # ── Vi Prepaid T&C ────────────────────────────────────────────────────────
    {
        "title": "Vi — Prepaid Plan Tariff and Grace Period",
        "text": (
            "Vi prepaid SIM cards do not carry any pre-loaded value and must be "
            "recharged with recharge cards available in different denominations. "
            "For limited validity plans, a grace period of 15 days is provided after "
            "expiry. During this grace period, the subscriber cannot make or receive "
            "calls, but the balance value remains available to the subscriber's credit "
            "for the initial 15 days and will not be accessible thereafter in case of "
            "recharge with talk-time or validity denominations. "
            "If the number is not used even once after activation, it will be barred "
            "within 7 days and may be permanently disconnected within 90 days."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Vi — Prepaid Non-Usage Disconnection and ANRS",
        "text": (
            "Vi prepaid services are discontinued after 90 days of no usage "
            "(no voice/video call, outgoing SMS, data upload/download, or VAS). "
            "For customers with no usage for 90 days and account balance ≥ Rs.20: "
            "Vi debits Rs.20 and extends the no-usage period by 30 days under the "
            "Automatic Number Retention Scheme (ANRS). This continues while the "
            "balance remains ≥ Rs.20. If balance falls below Rs.20, the number is "
            "disconnected. The customer can reactivate within 15 days of disconnection "
            "by paying Rs.20 reactivation charge. "
            "Postpaid Safe Custody: available for Rs.150 for 3 months — number "
            "retained, no usage/rental charges during this period."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Vi — Lost or Stolen SIM — Replacement Process",
        "text": (
            "If your Vi SIM card is lost, stolen, misplaced, or damaged, the entire "
            "liability rests with the customer. The customer must inform Vi immediately "
            "to suspend services. The loss or inability to use the SIM does not absolve "
            "the customer from paying outstanding charges. "
            "For SIM replacement: visit a Vi store with original ID and submit a written "
            "request or inform Vi via Customer Care. The same number can be given to "
            "the customer subject to positive validation as per existing records and "
            "applicable payment. SIM Exchange is a chargeable service available at any "
            "authorized Vi store."
        ),
        "category": "sim_esim",
    },
    # ── Vi VAS ────────────────────────────────────────────────────────────────
    {
        "title": "Vi — VAS — Activation, Charges, and Consumer Protections",
        "text": (
            "Vi Value Added Services (VAS) are offered at an additional per-minute, "
            "per-second, per-SMS, or per-download rate. Detailed VAS tariffs are "
            "available at www.MyVi.in. Vi is entitled to change, vary, alter, add, or "
            "withdraw any VAS and/or vary their charges at its sole discretion with "
            "notice within TRAI guidelines. "
            "Not all VAS may be available on a given connection. "
            "Consumers have the right to deactivate any VAS by contacting Vi Customer "
            "Care (198) or visiting www.MyVi.in. No VAS shall be provided without "
            "explicit customer consent per TRAI regulations."
        ),
        "category": "billing_recharge",
    },
    # ── Vi DND ────────────────────────────────────────────────────────────────
    {
        "title": "Vi — DND Registration — Do Not Disturb",
        "text": (
            "Vi customers can register for Do Not Disturb (DND) to restrict unwanted "
            "telemarketing SMS and calls. DND is activated immediately but is applicable "
            "after 24 hours. "
            "To register or change DND preferences: call or SMS 1909; use the Vi app; "
            "use IVR at 1909; or visit www.MyVi.in. "
            "DND preference codes: "
            "'FULLY BLOCK 0' — blocks all commercial calls/SMS. "
            "'BLOCK 1' — Banking/Insurance/Financial/Credit cards. "
            "'BLOCK 2' — Real Estate. 'BLOCK 3' — Education. "
            "'BLOCK 4' — Health. 'BLOCK 5' — Consumer goods and automobiles. "
            "'BLOCK 6' — Communication/Broadcasting/Entertainment/IT. "
            "'BLOCK 7' — Tourism and Leisure. 'BLOCK 8' — Food and Beverages. "
            "For DND-related support, call Vi at +91-9619500900 or visit "
            "https://www.vilpower.in."
        ),
        "category": "ivr_complaints",
    },
    # ── Vi Complaint Redressal ─────────────────────────────────────────────────
    {
        "title": "Vi — Customer Care Contact Details",
        "text": (
            "Vi customer care channels: "
            "Complaints: call 198 (toll free) from a Vi number. "
            "General information: call 199 from a Vi number. "
            "WhatsApp: message Vi at 9654297000. "
            "Email: customercare@vodafoneidea.com. "
            "Vi App: log complaints or raise service requests. "
            "Vi stores: visit any authorized Vi store for in-person support. "
            "For Vi postpaid tariff plan and product information, visit www.MyVi.in or "
            "the Vi app or any exclusive Vi store."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "Vi — Two-Stage Complaint Resolution — Contact Center and Appellate",
        "text": (
            "Vi operates a 2-stage complaint resolution system: "
            "Stage 1 — Contact Center / Showrooms: available 24x7 via 198 (toll free), "
            "Vi App, WhatsApp, email, or Vi store. A unique docket number is allotted "
            "to every complaint registered. "
            "Stage 2 — Appellate Authority: If unsatisfied with Stage 1 resolution, "
            "consumers may escalate to the Appellate Authority. The Appellate Authority "
            "will resolve the appeal within 39 days of receipt. "
            "Consumer rights: every consumer has the right to receive a unique docket "
            "number; approach the Appellate Authority for unresolved complaints; "
            "request Appellate Authority contact details from the Contact Center "
            "executive."
        ),
        "category": "ivr_complaints",
    },
    # ── Vi Disconnection / Rights ──────────────────────────────────────────────
    {
        "title": "Vi — Customer Rights — Termination and Refund",
        "text": (
            "Vi customers have the following rights regarding service termination: "
            "The consumer can terminate or disconnect services at their convenience. "
            "After termination, bills are checked, reconciliation is done, and any "
            "amount due after adjusting outstanding dues is returned from the security "
            "deposit. This process takes a maximum of 45 days from disconnection. "
            "Termination request methods: written request, fax, email, telephone call, "
            "or SMS to Vi. "
            "Termination is subject to the return or recovery of any customer premise "
            "equipment (CPE) where applicable."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Vi — Grounds for Immediate Service Termination by Vi",
        "text": (
            "Vi may immediately terminate services in any of these situations: "
            "Government, TRAI, or competent authority suspends, terminates, or takes "
            "over the license. Customer fails credit check or provides fraudulent "
            "information. Customer fails to pay subscription charges or dues. "
            "Customer breaches terms and does not remedy within 7 days of written notice. "
            "Customer uses services for unlawful, immoral, abusive, obscene, threatening, "
            "or harassing purposes. Customer's number is found used for promotional "
            "activity without registration as a telemarketer. "
            "Vi shall be entitled to recover all outstanding charges and dues from the "
            "customer upon termination."
        ),
        "category": "billing_recharge",
    },
    # ── Vi MNP ────────────────────────────────────────────────────────────────
    {
        "title": "Vi — MNP Timelines and UPC Generation",
        "text": (
            "The total time frame for Vi port activation is: "
            "2 working days for inter-circle porting; "
            "4 working days for intra-circle and corporate subscriber porting "
            "(excluding Sundays and national holidays). "
            "To obtain UPC: SMS PORT followed by your 10-digit mobile number to 1900. "
            "UPC is valid for 4 days. Porting charge: up to a maximum of Rs.6.46. "
            "A customer can withdraw the porting request within 24 hours of submission "
            "via SMS. If the port request is cancelled, the port fee (if charged) may "
            "not be refunded. Once ported-in to Vi, the number cannot be ported out "
            "before 90 days or any other duration prescribed by TRAI."
        ),
        "category": "sim_esim",
    },
    {
        "title": "Vi — MNP — Grounds for UPC Rejection",
        "text": (
            "Vi will reject a UPC generation request for porting out under the following "
            "conditions: outstanding payments due by way of pending bills; porting "
            "request made before 90 days from activation or last porting; change of "
            "ownership request is under process; the mobile number is sub-judice; "
            "porting prohibited by a Court of Law; UPC mismatch; subsisting contractual "
            "obligations not complied with; TAFCOP re-verification process pending; "
            "UPC validity has expired; corporate porting without authorization letter; "
            "request for more than 100 numbers; authorization letter issues such as "
            "missing seal, signature, or company name mismatch. "
            "Vi will communicate the reason for rejection to the subscriber."
        ),
        "category": "sim_esim",
    },
    # ── Vi Roaming ────────────────────────────────────────────────────────────
    {
        "title": "Vi — National Roaming — Operator-Specific Tariff Applies",
        "text": (
            "While roaming in other Vi-registered telecom circles, the applicable "
            "operator-specific tariffs will be charged for all services availed. "
            "National roaming charging is subject to the ceiling prescribed by TRAI. "
            "For Vi prepaid connections, Local, STD, ISD calls, SMS, national roaming, "
            "international roaming, Call Conference, and CLIP are activated by default. "
            "All STD, ISD, and roaming usage is charged depending on the location "
            "from which the call originated."
        ),
        "category": "roaming_international",
    },
    {
        "title": "Vi — International Roaming — Pre-Travel Checks",
        "text": (
            "Before embarking on international travel with a Vi connection, subscribers "
            "must verify applicable tariffs and charges for both voice and data by "
            "visiting a Vi store, the Vi App, or www.MyVi.in. "
            "Vi reserves the right to demand complete payment of the bill, including "
            "unbilled amounts, when international or national roaming is used. "
            "In case of sudden usage spikes on ISD/roaming services, Vi may apply "
            "credit limit protocols requiring advance payment before services continue. "
            "Foreign National customers will be allowed telecom services for only 90 "
            "days or until VISA expiry, whichever is earlier."
        ),
        "category": "roaming_international",
    },
    # ── Vi QoS ────────────────────────────────────────────────────────────────
    {
        "title": "Vi — TRAI Quality of Service Benchmarks",
        "text": (
            "Vi (Vodafone Idea) must meet the following TRAI-prescribed quality benchmarks: "
            "Metering and billing credibility (postpaid and prepaid): ≤0.1% complaints. "
            "Resolution of billing/charging complaints: 100% within 4 weeks. "
            "Adjustment to customer account after resolution: within 1 week. "
            "Call centre accessibility: ≥95%. "
            "Calls answered (voice to voice) within 90 seconds: ≥95%. "
            "Service termination / closure: 100% within ≤7 days. "
            "Refund of deposits after closure: 100% within 45 days. "
            "Vi strives to meet these benchmarks; deviations due to technical or "
            "practical reasons are duly reported to TRAI."
        ),
        "category": "ivr_complaints",
    },
    # ── Vi Duties ─────────────────────────────────────────────────────────────
    {
        "title": "Vi — Operator Duties — Tariff Plan Stability",
        "text": (
            "Vi (Vodafone Idea Limited) has the following obligations to subscribers: "
            "A tariff plan once offered is available to a subscriber for a minimum "
            "period of 6 months (or lifetime in case of lifetime validity plans). "
            "For lifetime/unlimited validity plans, Vi will communicate the month and "
            "year of expiry in promotional literature. "
            "Vi must give 30 days advance notice to TRAI and subscribers before "
            "terminating any existing tariff plan. "
            "Customers will be informed on activation of a recharge voucher about "
            "usage, account balance, and VAS charges, as per TRAI's Telecom Consumer "
            "Protection Regulation 2012. "
            "All plan details are available on the Vi website www.MyVi.in."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Vi — Telemarketer Number Restrictions for Subscribers",
        "text": (
            "Vi subscribers must not use their SIM for telemarketing purposes without "
            "registering as a telemarketer. If a Vi number is found to be used for "
            "unsolicited promotional activity without telemarketer registration: "
            "First offence: usage capped at 20 calls and 20 SMS per day for 30 days. "
            "Second offence: usage capped for 180 days. "
            "Third offence and beyond: the number and all numbers on the same name and "
            "address are disconnected and blacklisted for 2 years; new subscriptions "
            "are denied. Telemarketers must register on https://www.vilpower.in as per "
            "TCCCPR 2018 guidelines."
        ),
        "category": "ivr_complaints",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
#  CROSS-OPERATOR / TRAI REGULATORY PASSAGES
# ─────────────────────────────────────────────────────────────────────────────
REGULATORY_PASSAGES = [
    {
        "title": "TRAI — Outage Compensation — All Operators",
        "text": (
            "Under TRAI regulations, all Indian telecom operators (Jio, Airtel, Vi, "
            "BSNL) must compensate subscribers for significant network outages. A "
            "significant network outage is defined as services being unavailable in a "
            "district for more than 4 hours. The operator must report such outages to "
            "TRAI within 24 hours of the outage starting. "
            "Compensation (applicable for outages lasting more than 24 hours): "
            "Postpaid subscribers — proportional rent rebate based on plan charges for "
            "the number of affected days, credited in the next bill. "
            "Prepaid subscribers — validity of the subscribed tariff plan extended by "
            "the number of affected days."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "TRAI — Tariff Plan Protection — 6-Month Minimum Availability",
        "text": (
            "TRAI regulations require that a tariff plan, once offered to and enrolled "
            "by a subscriber, must remain available to that subscriber for a minimum "
            "period of 6 months from the date of enrollment. Operators must also give "
            "at least 30 days advance notice to TRAI and all enrolled subscribers "
            "before discontinuing any existing tariff plan. During the notice period, "
            "subscribers can freely migrate to any other available plan. No migration "
            "fee is chargeable for changing to any bill plan. Tariff increases on any "
            "item are not permitted within the first 6 months of enrollment."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "TRAI — MNP National Regulations — Key Rules for All Operators",
        "text": (
            "Mobile Number Portability (MNP) national rules applicable across all "
            "Indian telecom operators: "
            "MNP is available nationally across all operators within and between telecom "
            "circles. Porting is allowed only after 90 days from activation or last porting. "
            "To obtain UPC, SMS 'PORT <10-digit number>' to 1900. "
            "UPC validity: 4 days for most LSAs; 30 days for J&K, Assam, and North East. "
            "Maximum porting charge: Rs.6.46 paid to recipient operator. "
            "No service period: up to 2 hours during porting. "
            "Withdrawal: within 24 hours of port request submission. "
            "Prepaid balance and entitlements lapse upon porting out."
        ),
        "category": "sim_esim",
    },
    {
        "title": "TRAI — VAS Consumer Protection Rules — All Operators",
        "text": (
            "TRAI's VAS (Value Added Services) consumer protection rules apply to all "
            "Indian telecom operators: "
            "No chargeable VAS can be activated without explicit customer consent. "
            "A free VAS cannot be converted to a chargeable one without consent. "
            "No VAS can be activated via a single key-press on the handset. "
            "Subscribers must be notified at least 3 days before a VAS renewal, with "
            "the renewal date, charge, and toll-free unsubscription number. "
            "Accidental VAS activation: if a subscriber requests unsubscription within "
            "24 hours on grounds of accidental activation, the operator must deactivate "
            "and fully refund the charge. "
            "Universal deactivation channel: SMS/call to 155223 (toll free)."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "TRAI — UCC / DND National Rules — Commercial Communication Restrictions",
        "text": (
            "TRAI's Telecom Commercial Communications Customer Preference Regulations "
            "(TCCCPR 2018) govern all commercial communications in India: "
            "No telemarketing calls/SMS are permitted between 9:00 PM and 10:00 AM. "
            "All telemarketers must register on the DLT (Distributed Ledger Technology) "
            "portal before starting any telemarketing activity. "
            "Telemarketing voice calls use number series starting with 140XXXXXXXX. "
            "Transactional/service calls use number series starting with 1600XXXXXXXX. "
            "Subscribers can register DND preferences at 1909 (call/SMS) or ndnc.net.in. "
            "DND complaints: file within 7 days of receiving UCC by calling 1909 or "
            "forwarding the communication to 1909 with the sender number and date."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "TRAI — Complaint Redressal — Two-Level System and 39-Day Timeline",
        "text": (
            "TRAI mandates a two-level complaint redressal system for all Indian telecom "
            "operators under the Telecom Consumers Complaint Redressal Regulations 2012: "
            "Level 1 — Contact Center: Operators must provide 24/7 access, issue a "
            "unique docket number for every complaint, and resolve within TRAI timelines. "
            "Level 2 — Appellate Authority: Consumers who are not satisfied with Level "
            "1 resolution may appeal within 30 days of the expiry of the resolution "
            "time limit. The Appellate Authority must decide the appeal within 39 days "
            "of filing. A docket number must be issued within 3 days of filing. "
            "If Level 2 is also unresolved, consumers may escalate to TRAI's Consumer "
            "Complaint Portal."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "TRAI — Customer Service Benchmarks — Billing Dispute Resolution",
        "text": (
            "TRAI prescribes the following customer service benchmarks for all operators: "
            "Billing and charging complaints: ≤0.1% of subscriber base. "
            "Resolution of all billing/charging complaints: 100% within 4 weeks. "
            "Application of credit or adjustment to customer account: 100% within 1 "
            "week from date of complaint resolution or fault rectification. "
            "Call centre/customer care accessibility: ≥95%. "
            "Calls answered by operator (voice-to-voice) within 90 seconds: ≥95%. "
            "Service termination/closure within 7 working days of request: 100%. "
            "Security deposit refund within 45 days of closure: 100%."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "India — Maximum Mobile Connections Allowed Per Individual",
        "text": (
            "As per DoT (Department of Telecommunications) guidelines, an individual "
            "customer is not permitted to hold more than 9 mobile connections in total "
            "across all telecom service providers in India. This limit applies regardless "
            "of which operators the connections are with. If a customer already has 9 "
            "connections, no additional connection will be granted by any operator. "
            "Customers must declare at the time of applying for a new connection the "
            "number of mobile connections they already hold across all operators. "
            "Violations — undisclosed connections beyond 9 — can result in immediate "
            "disconnection of the excess connections."
        ),
        "category": "sim_esim",
    },
    {
        "title": "India — Telecom KYC and eKYC — Aadhaar OTP Verification",
        "text": (
            "All telecom SIM cards in India require KYC (Know Your Customer) verification "
            "as per DoT regulations. Aadhaar-based eKYC is the fastest method — the "
            "subscriber provides their Aadhaar number, an OTP is sent to the linked "
            "mobile, and digital verification is complete without visiting a store. "
            "Physical KYC requires submitting original ID proof documents at a carrier "
            "store. Acceptable identity proofs include Aadhaar, Passport, PAN Card, "
            "Voter ID, Driving License, Arms License, and government-issued photo IDs. "
            "Failure to complete KYC within 30 days results in suspension of outgoing "
            "services followed by full service deactivation."
        ),
        "category": "sim_esim",
    },
    {
        "title": "India — TAFCOP Portal — Checking Your Active Mobile Connections",
        "text": (
            "TAFCOP (Telecom Analytics for Fraud Management and Consumer Protection) is "
            "a DoT portal that allows subscribers to check all mobile connections "
            "registered in their name across all operators in India. "
            "Visit tafcop.dgtelecom.gov.in and log in with your mobile number to view "
            "active connections. If you find any unknown connections in your name, you "
            "can report them for deactivation via the portal. "
            "TAFCOP re-verification may also be initiated by operators if they suspect "
            "fraudulent use of a subscriber's identity. During TAFCOP re-verification, "
            "porting requests for the affected numbers are blocked."
        ),
        "category": "sim_esim",
    },
    {
        "title": "India — Telecom Security Rules — IMEI, SIM-BOX, and Illegal Devices",
        "text": (
            "Indian telecom law (Telecommunication Act 2023) strictly prohibits: "
            "Possession or use of equipment that blocks telecommunications without "
            "authorization; using telecom identifiers not allotted to you; tampering "
            "with IMEI or other telecom identifiers; possessing radio equipment without "
            "authorization that can accommodate more than the specified number of SIMs; "
            "obtaining SIM cards or telecom identifiers through fraud, cheating, or "
            "impersonation; using SIM-BOX devices. "
            "Violations are punishable under Section 42(3) of the Telecommunication "
            "Act 2023. Operators will disconnect any SIM used in a device with invalid "
            "or untraceable IMEI without prior notice."
        ),
        "category": "sim_esim",
    },
    {
        "title": "India — Fault Repair Benchmarks — Wireline and Broadband",
        "text": (
            "TRAI-prescribed fault repair benchmarks for wireline and broadband services "
            "across all operators: "
            "Fault incidences per 100 subscribers: ≤5 per quarter. "
            "Fault repair by next working day: ≥85%. "
            "Fault repair within 3 working days: ≥99%. "
            "Mean Time-To-Repair (MTTR): ≤10 hours. "
            "Compensation if fault is unrepaired after 3 working days: "
            "Postpaid — proportional rent rebate for days fault remained pending. "
            "Prepaid — validity extension equivalent to days fault remained pending. "
            "These benchmarks are assessed quarterly for wireline services."
        ),
        "category": "connectivity_5g",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
#  ASSEMBLY AND APPEND
# ─────────────────────────────────────────────────────────────────────────────
ALL_NEW_PASSAGE_GROUPS = [
    JIO_PASSAGES,
    AIRTEL_PASSAGES,
    VI_PASSAGES,
    REGULATORY_PASSAGES,
]


def append_to_corpus(
    output_dir: str = "data/raw/telecom_kb",
    start_id: int = 400,
) -> list[dict]:
    """
    Assembles new passages extracted from operator charters, assigns IDs
    starting at start_id, and APPENDS them to the existing passages.jsonl.
    Returns the list of new passage dicts.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    passages = []
    passage_id = start_id

    for group in ALL_NEW_PASSAGE_GROUPS:
        for p in group:
            passage = {
                "id":         f"tc_{passage_id:04d}",
                "title":      p["title"],
                "text":       p["text"].strip(),
                "category":   p["category"],
                "domain":     "telecom",
                "source":     "charter_pdf_v1",
                "char_count": len(p["text"].strip()),
            }
            passages.append(passage)
            passage_id += 1

    out_file = out / "passages.jsonl"
    with open(out_file, "a", encoding="utf-8") as f:
        for p in passages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    _print_summary(passages, out_file)
    return passages


def _print_summary(passages: list[dict], out_file: Path) -> None:
    from collections import Counter
    cats = Counter(p["category"] for p in passages)
    ops = Counter(
        "jio" if "Jio" in p["title"] or "JioFiber" in p["title"]
        else "airtel" if "Airtel" in p["title"]
        else "vi" if "Vi —" in p["title"]
        else "trai/regulatory"
        for p in passages
    )

    print("\n" + "=" * 56)
    print(" Telecom Charter Passages — Append Summary")
    print("=" * 56)
    print(f" New passages added : {len(passages)}")
    print(f" Output file        : {out_file}")
    print(f" ID range           : {passages[0]['id']} → {passages[-1]['id']}")
    print("-" * 56)
    print(" New passages by category:")
    for cat, count in sorted(cats.items()):
        bar = "█" * count
        print(f"  {cat:<32} {count:>3}  {bar}")
    print("-" * 56)
    print(" New passages by operator source:")
    for op, count in sorted(ops.items()):
        print(f"  {op:<32} {count:>3}")
    print("=" * 56)
    print(" Next: python -m src.ingestion.kb_builder")
    print("=" * 56 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Append operator charter passages to telecom KB"
    )
    parser.add_argument(
        "--output_dir",
        default="data/raw/telecom_kb",
        help="Directory containing passages.jsonl to append to",
    )
    parser.add_argument(
        "--start_id",
        type=int,
        default=400,
        help="Starting ID for new passages (must be > last existing ID)",
    )
    args = parser.parse_args()

    append_to_corpus(args.output_dir, args.start_id)