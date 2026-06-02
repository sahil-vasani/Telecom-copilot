"""
telecom_corpus_builder.py

Generates a telecom-specific knowledge base with 360+ passages
covering all 6 support categories. No internet connection required.

Output:
    data/raw/telecom_kb/passages.jsonl   ← one JSON object per line

Each passage:
    {
        "id":       "tc_001",
        "title":    "Enabling 5G on Android",
        "text":     "...",
        "category": "connectivity_5g",
        "domain":   "telecom",
        "source":   "corpus_builder_v1"
    }

Usage:
    python telecom_corpus_builder.py
    python telecom_corpus_builder.py --output_dir data/raw/telecom_kb
"""

import json
import argparse
from pathlib import Path
from  data_source.bsnl_data_ingestion import BSNL_CHARTER_PASSAGES
from  data_source.jio_data_ingestion import JIO_FAQ_DATA
from  data_source.airtel_data_ingestion import AIRTEL_FAQ_DATA
from data_source.vi_data_ingestion import VI_FAQ_DATA
from data_source.TRAI_data_ingestion import TRAI_PASSGES
from data_source.general_ingestion import NEW_GENERAL_PASSAGES
# ────────────────
#  CATEGORY 1 : 5G / 4G Connectivity  (80 passages)
# ─────────────────────────────────────────────────────────────
CONNECTIVITY_PASSAGES = [
    {
        "title": "Enabling 5G on Android",
        "text": (
            "To enable 5G on an Android phone, open Settings and go to Connections "
            "or Network & Internet. Tap Mobile Networks, then select Preferred Network "
            "Type. Choose 5G/4G/3G/2G (auto) or NR/LTE Auto. If 5G is not listed, your "
            "device may not support 5G or your SIM plan may not include 5G access. Contact "
            "your carrier to confirm 5G eligibility on your account."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "5G Shows but No Internet",
        "text": (
            "If your phone shows a 5G icon but you cannot browse the internet, first check "
            "that mobile data is turned on in Settings. Then verify your APN settings are "
            "correct for your carrier. Toggle Airplane Mode on for 30 seconds and then off. "
            "Restart the phone. If the problem persists, remove and reinsert the SIM card. "
            "5G coverage may be limited to certain areas — check your carrier's 5G map."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "5G vs 4G LTE — What is the Difference",
        "text": (
            "5G (New Radio, NR) offers significantly faster speeds than 4G LTE, with peak "
            "theoretical speeds of 20 Gbps versus 1 Gbps for LTE. 5G also provides lower "
            "latency (1ms vs 30-50ms for LTE). However, 5G coverage is still being expanded. "
            "In areas without 5G, your phone will automatically fall back to 4G LTE. "
            "NSA (Non-Standalone) 5G uses the 4G core network, while SA (Standalone) 5G "
            "uses a full 5G core and supports features like network slicing."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "How to Fix 4G LTE Dropping to 3G",
        "text": (
            "If your phone frequently drops from 4G LTE to 3G or H+, try these steps: "
            "First, restart your phone. Go to Settings > Mobile Networks > Network Mode "
            "and select LTE/4G only or 4G/3G/2G auto. Check if you are in a low-coverage "
            "area by looking at the signal bars. Update your carrier settings if prompted. "
            "Reset network settings (this will remove saved Wi-Fi passwords). If the issue "
            "continues, contact your carrier for a network coverage check at your location."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "No Signal on Phone — Troubleshooting",
        "text": (
            "If your phone shows No Service or No Signal, follow these steps: "
            "1. Toggle Airplane Mode on, wait 15 seconds, then toggle it off. "
            "2. Restart the device. "
            "3. Remove and reinsert the SIM card after powering off the phone. "
            "4. Go to Settings > Mobile Networks > Network Operators and tap Search Networks. "
            "5. Select your carrier manually. "
            "6. Check if your SIM is activated — call customer care from another phone. "
            "7. Visit a carrier store for a SIM replacement if the SIM is damaged."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "Mobile Data Not Working After Recharge",
        "text": (
            "If mobile data stops working after a recharge, first confirm the recharge "
            "was successful by checking your balance via *121# or the carrier app. "
            "Restart your device after the recharge. Verify that mobile data is enabled "
            "in Settings. Check if your plan includes a daily data limit — once exhausted, "
            "speeds may be throttled. If you recharged a wrong plan, contact customer "
            "care immediately with your transaction ID for resolution."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "VoLTE — Voice over LTE Setup",
        "text": (
            "VoLTE (Voice over LTE) enables HD voice calls over the 4G network. "
            "To enable VoLTE: Go to Settings > Mobile Networks and toggle VoLTE Calls on. "
            "Your SIM must support VoLTE, your plan must include it, and you must be in a "
            "VoLTE coverage area. If VoLTE is not visible in settings, your device may not "
            "support it. VoLTE calls maintain your 4G data connection during calls, unlike "
            "older CSFB (Circuit-Switched Fallback) which drops to 2G/3G for voice."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "Slow Internet Speed Despite Full Signal",
        "text": (
            "Full signal bars indicate strong signal strength but not necessarily high "
            "speed. Speed depends on network congestion, your data plan speed tier, "
            "and whether your daily data limit is exhausted. To diagnose: Run a speed "
            "test at fast.com. Check your daily usage via *121#. Try a different time "
            "of day (peak hours cause congestion). Toggle between 5G and 4G to compare. "
            "Clear app caches. If the issue persists during off-peak hours, raise a "
            "network complaint with your carrier."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "Wi-Fi Calling Setup and Troubleshooting",
        "text": (
            "Wi-Fi Calling allows voice calls over a Wi-Fi network when cellular signal "
            "is weak. To enable: Settings > Mobile Networks > Wi-Fi Calling (toggle on). "
            "Your carrier must support Wi-Fi Calling and your account must be enabled. "
            "Calls made over Wi-Fi Calling are charged as regular calls. If calls drop "
            "when switching between Wi-Fi and cellular, enable seamless handover in "
            "Wi-Fi Calling settings. Emergency calls (112) should still work even on "
            "Wi-Fi Calling."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "Network Congestion and Throttling",
        "text": (
            "Network throttling occurs when you exhaust your high-speed data allowance. "
            "After the limit is reached, speeds are reduced to 64 Kbps or 128 Kbps "
            "depending on your plan. Throttled speeds are sufficient for text messaging "
            "but not for video streaming. To restore full speed, purchase an add-on data "
            "pack via the carrier app or by dialing the add-on recharge code. Network "
            "congestion (not throttling) occurs during peak hours and is temporary."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "How to Check Network Band in Use",
        "text": (
            "To check which frequency band your phone is connected to, enable Developer "
            "Options by tapping Build Number 7 times in About Phone. Go to Developer "
            "Options > Network type and signal. Alternatively, use apps like Network "
            "Cell Info or LTE Discovery. Common 5G bands in India: Band 78 (3.5 GHz, "
            "high speed, short range), Band 28 (700 MHz, long range, good indoors). "
            "Understanding your band helps diagnose coverage issues."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "IMEI Number — What It Is and How to Find It",
        "text": (
            "The IMEI (International Mobile Equipment Identity) is a unique 15-digit "
            "number identifying your device. Dial *#06# to display it. You can also find "
            "it in Settings > About Phone > IMEI. The IMEI is needed when reporting a "
            "lost/stolen phone, claiming warranty, or unlocking a device. "
            "Carriers can block a stolen phone's IMEI using the CEIR portal. "
            "A dual-SIM phone has two IMEIs. Never share your IMEI with untrusted parties."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "Carrier Network Selection — Manual vs Automatic",
        "text": (
            "In automatic network mode, your phone selects the best available network. "
            "In manual mode, you choose the carrier. Manual selection is useful when "
            "automatic selection picks a weaker network. To switch: Settings > Mobile "
            "Networks > Network Operators > Search Networks. Select your carrier from the "
            "list. If you see Forbidden when selecting, your SIM is not allowed on that "
            "network. Roaming SIMs may need manual selection for specific partners."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "Dual SIM Network Management",
        "text": (
            "On a dual-SIM phone, go to Settings > SIM Card Manager to assign: "
            "Default SIM for calls, default SIM for SMS, default SIM for mobile data. "
            "You can enable data switching (automatically use SIM 2 when SIM 1 has no "
            "signal). Only one SIM can use 5G at a time on most phones. The non-5G SIM "
            "will operate on 4G or lower. Set your primary SIM to the one with the best "
            "plan for data to avoid unexpected charges."
        ),
        "category": "connectivity_5g",
    },
    {
        "title": "Ping and Latency Issues on Mobile Network",
        "text": (
            "High ping (latency) on mobile networks affects gaming and video calls. "
            "Typical latency: 4G LTE = 30-50ms, 5G NSA = 15-30ms, 5G SA = 1-5ms. "
            "To reduce latency: Use 5G if available, connect to Wi-Fi for gaming, "
            "close background apps consuming data, disable VPN if active. "
            "If ping is consistently high (>100ms) on a good signal, it may indicate "
            "network congestion at your tower. Report to carrier with location details."
        ),
        "category": "connectivity_5g",
    },
]  # Add more passages to reach 80 — template continues below

# ─────────────────────────────────────────────────────────────
#  CATEGORY 2 : APN Settings  (60 passages)
# ─────────────────────────────────────────────────────────────
APN_PASSAGES = [
    {
        "title": "What is an APN Setting",
        "text": (
            "APN stands for Access Point Name. It is a gateway between your carrier's "
            "mobile network and the public internet. Your phone needs the correct APN "
            "settings to connect to mobile data, send MMS, and use certain carrier "
            "services. APN settings include: Name, APN (the gateway address), Proxy, "
            "Port, MMSC (for MMS), MMS Proxy, MMS Port, MCC (Mobile Country Code), "
            "MNC (Mobile Network Code), and Authentication Type."
        ),
        "category": "apn_settings",
    },
    {
        "title": "Jio APN Settings for Android",
        "text": (
            "To configure Jio 4G/5G APN on Android: Go to Settings > Connections > "
            "Mobile Networks > Access Point Names. Tap + to add new APN. "
            "Name: Jio 4G, APN: jionet, Proxy: leave blank, Port: leave blank, "
            "Username: leave blank, Password: leave blank, Server: leave blank, "
            "MMSC: http://mmsc.jio.com, MMS Proxy: 192.168.101.1, MMS Port: 8080, "
            "MCC: 404, MNC: 50, Authentication type: None, APN type: default,supl,mms. "
            "Save and restart the device."
        ),
        "category": "apn_settings",
    },
    {
        "title": "Airtel APN Settings for Android",
        "text": (
            "To configure Airtel 4G APN on Android: Settings > Connections > Mobile "
            "Networks > Access Point Names > Add new. "
            "Name: Airtel, APN: airtelgprs.com, Proxy: blank, Port: blank, "
            "Username: blank, Password: blank, MMSC: http://100.1.201.171:10021/mmsc, "
            "MMS Proxy: 100.1.201.171, MMS Port: 8799, MCC: 404, MNC: 10 (varies by "
            "circle — check your circle code), Authentication: None, "
            "APN type: default,supl,mms. Save and restart."
        ),
        "category": "apn_settings",
    },
    {
        "title": "Vi (Vodafone Idea) APN Settings",
        "text": (
            "Vi 4G APN settings for Android: Name: Vi Internet, APN: portalnmms, "
            "Proxy: blank, Port: blank, Username: blank, Password: blank, "
            "MMSC: http://mms1.live.vodafone.in/mms/, MMS Proxy: 10.10.1.100, "
            "MMS Port: 9401, MCC: 404, MNC: 20, Authentication: None, "
            "APN type: default,supl,mms. Alternatively try APN: www for basic internet. "
            "Save and reboot. If MMS fails, try MMSC: http://10.10.1.100/mmsc."
        ),
        "category": "apn_settings",
    },
    {
        "title": "BSNL APN Settings",
        "text": (
            "BSNL 4G APN settings: Name: BSNL Internet, APN: bsnlnet, "
            "Proxy: blank, Port: blank, Username: blank, Password: blank, "
            "MMSC: http://www.bsnlmmsc.com/, MMS Proxy: 10.1.127.110, "
            "MMS Port: 8080, MCC: 404, MNC: 07, Authentication: None, "
            "APN type: default,supl,mms. For BSNL 3G fallback use APN: bsnlnet. "
            "If connection fails, try APN: bsnl.in as alternative."
        ),
        "category": "apn_settings",
    },
    {
        "title": "APN Settings for iOS iPhone",
        "text": (
            "On iPhone, APN settings are usually configured automatically when you "
            "insert a carrier SIM. If not: Go to Settings > Cellular > Cellular Data "
            "Network. Enter APN details provided by your carrier. If the Cellular Data "
            "Network option is not visible, go to Settings > General > VPN & Device "
            "Management and check for a carrier profile. Some carriers require installing "
            "a carrier settings update (Settings > General > About — tap Update if prompted)."
        ),
        "category": "apn_settings",
    },
    {
        "title": "APN Reset to Default",
        "text": (
            "If you have corrupted APN settings and cannot connect to mobile data, "
            "you can reset to default: Android — Settings > Mobile Networks > Access "
            "Point Names > tap the three-dot menu > Reset to Default. This will remove "
            "all custom APNs and restore carrier defaults. If the carrier default APN is "
            "incorrect, your carrier can push the correct APN via an OTA (Over-the-Air) "
            "configuration update. Call customer care and request an APN settings push."
        ),
        "category": "apn_settings",
    },
    {
        "title": "MMS Not Sending — APN Fix",
        "text": (
            "If MMS (picture/video messages) are not sending, check your MMSC, "
            "MMS Proxy, and MMS Port settings in your APN. Also ensure: Mobile Data "
            "is ON (MMS does not work over Wi-Fi on most phones), your plan includes "
            "MMS, and the APN type includes 'mms'. Check that MMS message size limit "
            "matches your carrier (usually 1MB-5MB). If settings are correct, toggle "
            "mobile data off and on. Try removing and reinserting the SIM."
        ),
        "category": "apn_settings",
    },
    {
        "title": "APN Cannot Be Edited — Greyed Out",
        "text": (
            "If the APN settings are greyed out and cannot be edited, your carrier has "
            "locked the APN via a SIM card restriction. This is common on branded/operator "
            "phones. Solutions: Contact your carrier to unlock APN editing, use a different "
            "SIM, or install the carrier's official APN profile if available. On Android, "
            "if you have Developer Options enabled, you may be able to bypass this via "
            "Settings > Developer Options > Restrict Background Data."
        ),
        "category": "apn_settings",
    },
    {
        "title": "Difference Between APN Types",
        "text": (
            "APN Type specifies what the APN is used for: "
            "default — general internet browsing, "
            "supl — Secure User Plane Location for GPS assistance, "
            "mms — Multimedia Messaging Service (picture messages), "
            "dun — Dial-Up Networking for tethering/hotspot, "
            "ims — IP Multimedia Subsystem, required for VoLTE. "
            "Setting APN type to 'default,supl,mms,ims' covers most use cases. "
            "Some carriers require a separate IMS APN for VoLTE to work."
        ),
        "category": "apn_settings",
    },
    {
        "title": "Mobile Hotspot APN — Tethering Issues",
        "text": (
            "If your mobile hotspot works but connected devices cannot access the "
            "internet, you may need a separate 'dun' APN for tethering. "
            "Create a new APN with APN type: dun, and the same APN address as your "
            "default APN. Some carriers block tethering unless you have a hotspot add-on. "
            "Contact your carrier to confirm tethering is enabled on your plan. "
            "Note: Jio and Airtel include tethering in most postpaid plans."
        ),
        "category": "apn_settings",
    },
    {
        "title": "5G APN Settings — New Radio Configuration",
        "text": (
            "5G SA (Standalone) may require updated APN settings compared to 4G. "
            "For Jio 5G: APN remains jionet but ensure APN protocol is set to IPv4/IPv6. "
            "For Airtel 5G: APN is airtelgprs.com, protocol IPv4/IPv6. "
            "Set Bearer to 5G NR or unspecified (auto). If 5G data doesn't work, "
            "delete existing APNs and add fresh ones. Set APN protocol to IPv6 if "
            "IPv4/IPv6 doesn't work — 5G SA cores often prefer IPv6."
        ),
        "category": "apn_settings",
    },
]

# ─────────────────────────────────────────────────────────────
#  CATEGORY 3 : Recharge & Billing  (70 passages)
# ─────────────────────────────────────────────────────────────
BILLING_PASSAGES = [
    {
        "title": "How to Check Prepaid Balance",
        "text": (
            "To check your prepaid balance and data usage: "
            "Jio: Open MyJio app or dial *333#. "
            "Airtel: Open Airtel Thanks app or dial *121#. "
            "Vi: Open Vi app or dial *111#. "
            "BSNL: Dial *123# or *124# for data balance. "
            "You can also check balance via the carrier's website after logging in "
            "with your mobile number. Balance includes talktime, data, SMS allowance, "
            "and plan validity remaining days."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Recharge Failed — Money Deducted but Plan Not Activated",
        "text": (
            "If your recharge payment was deducted but the plan was not activated: "
            "1. Wait 15-30 minutes — some recharges take time to process. "
            "2. Check your bank statement for the deduction and note the transaction ID. "
            "3. Contact customer care with the transaction ID, date, time, and amount. "
            "4. The carrier will verify and either activate the plan or issue a refund "
            "within 5-7 business days. "
            "5. Do NOT recharge again immediately — you may be double-charged. "
            "6. If paid via UPI, check the UPI app for payment status."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Postpaid Bill Higher Than Expected",
        "text": (
            "If your postpaid bill is higher than expected: "
            "1. Log in to the carrier app and view itemized bill details. "
            "2. Check for: excess data usage beyond plan limit, ISD/international calls, "
            "roaming charges, premium SMS subscriptions (VAS), or late payment fees. "
            "3. If you find unauthorized charges, raise a billing dispute online or "
            "call customer care. "
            "4. For VAS charges, type STOP to the shortcode or unsubscribe via *155223#. "
            "5. Request a detailed CDR (Call Detail Record) if charges are disputed."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "How to Stop Unwanted VAS Subscriptions",
        "text": (
            "VAS (Value Added Services) like caller tunes, daily jokes, or news alerts "
            "may cause surprise charges on your bill. To stop them: "
            "Dial 155223 (national DND helpline) or *155223#. "
            "SMS STOP to the shortcode that sends you the content. "
            "Use the carrier app: My Plans > Active Services > Deactivate. "
            "You can also register on the DND (Do Not Disturb) portal at "
            "ndnc.net.in to block promotional SMS and calls. "
            "VAS providers must stop service within 24 hours of your STOP request."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Auto-Renewal Recharge — How It Works",
        "text": (
            "Auto-renewal automatically recharges your prepaid plan when it expires, "
            "deducting the plan amount from your linked payment method. To enable: "
            "Open carrier app > My Plan > Enable Auto-Renewal and add a payment method. "
            "You will receive an SMS 3 days before renewal. To disable auto-renewal, "
            "go to the same section and toggle it off. Auto-renewal fails if your "
            "payment method has insufficient balance — you will receive an alert SMS."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Postpaid Plan — How to Generate Invoice",
        "text": (
            "To get your postpaid invoice: Open the carrier app > Bills & Payments > "
            "Download Bill. Choose the billing cycle month and download as PDF. "
            "Bills are generated on your bill date (usually fixed per account) and "
            "the due date is typically 18-21 days after the bill date. "
            "You can also view invoices online at the carrier website > My Account > "
            "View/Download Bill. GST invoice is available for business accounts "
            "with GSTIN registration."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Recharge Via UPI — Troubleshooting",
        "text": (
            "If UPI recharge fails: "
            "1. Check your UPI app (Google Pay, PhonePe, BHIM) for payment status. "
            "2. If it shows Pending, wait 24 hours — UPI pending transactions auto-resolve. "
            "3. If it shows Failed but money was deducted, it will be refunded in 5-7 days. "
            "4. Ensure your UPI PIN is correct and daily transaction limit is not exceeded. "
            "5. Try a different UPI app or use net banking/credit card as alternative. "
            "6. Keep the UPI transaction reference number for dispute tracking."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Data Add-On Packs — How to Activate",
        "text": (
            "If your daily data limit is exhausted, buy an add-on data pack: "
            "Jio: MyJio app > Plans > Add-Ons, or dial *333# option 4. "
            "Airtel: Airtel Thanks app > Add-Ons, or dial *121# option 4. "
            "Vi: Vi app > Data Add-On, or dial *111#. "
            "Add-ons activate instantly after payment and expire at plan end or in 30 "
            "days, whichever is earlier. Add-ons do not extend plan validity."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Bill Dispute — How to Raise a Complaint",
        "text": (
            "To dispute a charge on your telecom bill: "
            "1. Call customer care and quote the specific charge and date. "
            "2. Ask for a docket/complaint number — note it down. "
            "3. Resolution time is 30 days per TRAI regulations. "
            "4. If unresolved, escalate to the Appellate Authority. "
            "5. If still unresolved after 3 months, file a complaint at "
            "consumerforum.gov.in or TRAI's CGPDTM portal. "
            "6. For bills above Rs 1000 in dispute, you can withhold the disputed "
            "amount and pay the undisputed portion."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Missed Call Recharge — How It Works",
        "text": (
            "Some carriers allow recharge by giving a missed call to a specific number. "
            "The recharge amount is deducted from your account or linked bank account. "
            "This requires prior registration of a payment method. "
            "To use missed call recharge: Register your bank account via the carrier app. "
            "Give a missed call to the designated number (e.g., Airtel: 8800099123). "
            "You will receive an SMS confirmation. "
            "This service requires a minimum account balance of Rs 10."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "GST on Telecom Bills",
        "text": (
            "Telecom services attract 18% GST in India. This is applied to: "
            "monthly plan charges, add-on data packs, roaming charges, and ISD calls. "
            "Your bill shows base charge + SGST (9%) + CGST (9%) or IGST (18%) if "
            "inter-state. If you have a GSTIN (business), register it in your account "
            "to receive GST-compliant invoices for ITC (Input Tax Credit) claims. "
            "GST is NOT applied to handset purchases separately billed by the carrier."
        ),
        "category": "billing_recharge",
    },
    {
        "title": "Talktime Loans — Emergency Credit",
        "text": (
            "If you run out of balance and need to make an urgent call, you can request "
            "an emergency talktime loan: "
            "Airtel: Dial *141# > Emergency Credit. "
            "Jio: Dial *333# > Emergency Loan (available after 90 days of usage). "
            "Vi: Dial *119*2# for loan. "
            "BSNL: Dial *124*6#. "
            "Loans are repaid automatically on next recharge. Eligibility depends on "
            "your account history. Loan amounts range from Rs 5 to Rs 50."
        ),
        "category": "billing_recharge",
    },
]

# ─────────────────────────────────────────────────────────────
#  CATEGORY 4 : Roaming & International  (60 passages)
# ─────────────────────────────────────────────────────────────
ROAMING_PASSAGES = [
    {
        "title": "How to Activate International Roaming",
        "text": (
            "To activate international roaming before travelling abroad: "
            "Jio: Open MyJio > Plans > International Plans, choose a roaming pack. "
            "Airtel: Airtel Thanks app > International Roaming > Activate. "
            "Vi: Vi app > International > Roaming Packs. "
            "Activation can also be done by calling customer care or SMS. "
            "Roaming must be activated at least 24 hours before departure. "
            "Without a roaming pack, standard per-minute and per-MB charges apply "
            "and can be very high. Ensure your phone is not SIM-locked."
        ),
        "category": "roaming_international",
    },
    {
        "title": "Roaming Charges — Calls and Data",
        "text": (
            "Without a roaming pack, standard roaming rates apply: "
            "Incoming calls: Rs 1-5 per minute (varies by country). "
            "Outgoing calls to India: Rs 5-25 per minute. "
            "Outgoing local calls abroad: Rs 3-20 per minute. "
            "Data: Rs 10-50 per MB. "
            "SMS to India: Rs 5 per SMS. "
            "With a roaming pack, you get bundled minutes, data, and SMS at "
            "much lower rates. Always activate a pack before travelling. "
            "Data roaming should be turned off when not in use to avoid bill shock."
        ),
        "category": "roaming_international",
    },
    {
        "title": "How to Turn Off Data Roaming to Avoid Charges",
        "text": (
            "To prevent unexpected data charges while abroad: "
            "Android: Settings > Connections > Mobile Networks > disable Data Roaming. "
            "iPhone: Settings > Cellular > Cellular Data Options > disable Roaming. "
            "Keep Data Roaming off unless you have an active roaming pack. "
            "Even with roaming off, you can use Wi-Fi for internet access. "
            "Disable automatic app updates, background refresh, and cloud sync to "
            "prevent accidental data usage when you turn roaming on briefly."
        ),
        "category": "roaming_international",
    },
    {
        "title": "ISD Calls — International Calling from India",
        "text": (
            "To make an ISD (International Subscriber Dialing) call from India: "
            "Dial: 00 + country code + area code + number, or "
            "+ + country code + number (press and hold 0 for +). "
            "Example to call UK: 00 44 20 XXXX XXXX. "
            "ISD calls are charged per minute at country-specific rates. "
            "Cheaper alternatives: ISD packs (available from all carriers), "
            "WhatsApp/Facetime over Wi-Fi (free), calling cards, VoIP apps like Skype. "
            "Check rates at *121# or carrier app before calling."
        ),
        "category": "roaming_international",
    },
    {
        "title": "Roaming Pack vs Local SIM — Which Is Better",
        "text": (
            "Roaming pack: Convenient, no SIM change, keep your Indian number, "
            "contacts can reach you. Downside: Higher cost than local SIM. "
            "Local SIM: Cheapest data and calls, get a local number. Downside: "
            "You need an unlocked phone, lose your Indian number temporarily, "
            "contacts cannot reach your Indian number. "
            "Recommendation: For trips under 7 days, use a roaming pack. "
            "For longer trips, a local SIM or an eSIM data plan may be cheaper. "
            "eSIM options like Airalo offer data-only plans for 200+ countries."
        ),
        "category": "roaming_international",
    },
    {
        "title": "Roaming Not Working Abroad — Fix",
        "text": (
            "If your phone has no service abroad: "
            "1. Confirm roaming is activated on your account. "
            "2. Enable Data Roaming in phone settings. "
            "3. Set network selection to Automatic (not locked to Indian carrier). "
            "4. Try manual network selection and choose a local carrier. "
            "5. Ensure your plan has not expired. "
            "6. SIM may not support the local frequency bands — check compatibility. "
            "7. Call customer care from a local phone: provide your Indian number "
            "and location for remote diagnosis."
        ),
        "category": "roaming_international",
    },
    {
        "title": "Incoming Calls While Roaming",
        "text": (
            "When roaming abroad, people calling your Indian number will reach you "
            "normally — they pay Indian local call rates. You pay incoming call charges "
            "in the country you are visiting. With most roaming packs, incoming calls "
            "are free or at reduced rates. Check your pack details before travel. "
            "If you do not have a roaming pack, divert your calls to voicemail before "
            "travelling to avoid high incoming charges. "
            "Missed call alerts work on most networks even without data roaming."
        ),
        "category": "roaming_international",
    },
    {
        "title": "Airtel World Pass — International Roaming Pack",
        "text": (
            "Airtel World Pass packs offer bundled minutes, data, and SMS for "
            "international travel. Available for single country or multi-country. "
            "Example: Airtel USA/Canada pack at Rs 3,999 for 30 days includes "
            "3GB data, 100 minutes outgoing. "
            "Activate via Airtel Thanks app > International Roaming. "
            "Airtel IQ allows incoming calls to be free on select packs. "
            "Data is provided via partner networks — ensure Network Selection is Auto. "
            "Unused data/minutes do not carry over after the pack expires."
        ),
        "category": "roaming_international",
    },
    {
        "title": "Jio International Roaming Plans",
        "text": (
            "Jio's international roaming plans (JioInternational Packs) are available "
            "in MyJio app under International Plans. Packs include ISD minutes, data, "
            "and free incoming calls in select countries. "
            "Jio uses partner networks abroad — quality depends on the local partner. "
            "Jio Postpaid: Roaming is automatically available; outright charges apply "
            "without a pack. "
            "Jio Prepaid: Roaming must be activated and a pack must be active. "
            "Jio does not support roaming in all countries — check the list in the app."
        ),
        "category": "roaming_international",
    },
]

# ─────────────────────────────────────────────────────────────
#  CATEGORY 5 : SIM Activation / MNP / eSIM  (50 passages)
# ─────────────────────────────────────────────────────────────
SIM_PASSAGES = [
    {
        "title": "How to Activate a New SIM Card",
        "text": (
            "After getting a new SIM card, insert it into your phone and power it on. "
            "You should receive a welcome SMS within 4 hours. If not activated: "
            "1. Call customer care from another number with your new SIM number. "
            "2. Complete KYC verification if not done (Aadhaar OTP or in-store biometric). "
            "3. For Jio: call 1977 from your new SIM. For Airtel: visit a store. "
            "4. New SIM activation takes up to 24 hours for full network registration. "
            "5. If still inactive after 24 hours, visit the nearest carrier store."
        ),
        "category": "sim_esim",
    },
    {
        "title": "Mobile Number Portability — How to Port Your Number",
        "text": (
            "To port your mobile number to another carrier (MNP — Mobile Number Portability): "
            "1. SMS PORT <your 10-digit mobile number> to 1900 from your current SIM. "
            "2. You will receive a UPC (Unique Porting Code) — valid for 15 days. "
            "3. Visit the new carrier's store with your UPC, Aadhaar, and a passport photo. "
            "4. Submit the porting application. "
            "5. Porting is completed within 3 working days. "
            "6. Your number will be inactive for 2-4 hours during porting. "
            "7. You cannot port if your account has dues, or if you ported in the last 90 days."
        ),
        "category": "sim_esim",
    },
    {
        "title": "eSIM — What It Is and How to Activate",
        "text": (
            "eSIM (Embedded SIM) is a digital SIM built into your device — no physical SIM. "
            "Compatible devices: iPhone XS and later, Samsung Galaxy S20+, Pixel 3+, etc. "
            "To activate eSIM with Jio: open MyJio app > Get eSIM > scan QR code. "
            "For Airtel: open Thanks app > My Account > Get eSIM > complete KYC. "
            "For Vi: call 199 from any number or visit a store. "
            "eSIM can coexist with a physical SIM for dual-SIM functionality. "
            "eSIM cannot be physically transferred between phones — it must be re-provisioned."
        ),
        "category": "sim_esim",
    },
    {
        "title": "SIM Card Not Detected — Troubleshooting",
        "text": (
            "If your phone shows No SIM Detected or SIM Card Error: "
            "1. Power off the phone, remove the SIM, clean with a dry cloth, reinsert. "
            "2. Check if the SIM is seated properly in the tray (correct orientation). "
            "3. Try the SIM in another phone to rule out SIM damage. "
            "4. Try another SIM in your phone to rule out tray damage. "
            "5. Check for SIM tray physical damage. "
            "6. Go to Settings > About Phone to see if SIM is detected in software. "
            "7. If SIM works in another phone, yours may need repair. Visit a service center."
        ),
        "category": "sim_esim",
    },
    {
        "title": "SIM Upgrade — 3G to 4G or 4G to 5G",
        "text": (
            "To upgrade your SIM from 3G to 4G or 4G to 5G, visit your carrier's store "
            "with your phone and original ID proof. The upgrade is usually free. "
            "Your number and account balance are transferred to the new SIM. "
            "For Jio 5G SIM: visit a Jio store with Aadhaar — upgrade takes 15 minutes. "
            "For Airtel 5G: Airtel Claims most 4G SIMs work on 5G with a network update. "
            "After SIM upgrade, update APN settings and restart device. "
            "Incoming calls will be routed to the new SIM automatically within 2 hours."
        ),
        "category": "sim_esim",
    },
    {
        "title": "SIM Blocking — Lost or Stolen Phone",
        "text": (
            "If your phone is lost or stolen: "
            "1. Immediately call customer care to block the SIM. "
            "2. Airtel: 121, Jio: 198, Vi: 111, BSNL: 1503. "
            "3. Request both SIM block and IMEI block. "
            "4. IMEI blocking is done via the CEIR (Central Equipment Identity Register) "
            "portal at ceir.gov.in. "
            "5. File an FIR at the nearest police station. "
            "6. To get a replacement SIM with the same number, visit the carrier store "
            "with FIR copy and ID proof. SIM replacement takes 4-24 hours."
        ),
        "category": "sim_esim",
    },
    {
        "title": "Number Verification — OTP Not Received",
        "text": (
            "If you are not receiving OTP on your mobile number: "
            "1. Check signal strength — poor signal delays SMS. "
            "2. Check if DND (Do Not Disturb) is active — it may block OTP SMSes. "
            "3. Clear SMS app cache. "
            "4. Restart the device. "
            "5. Confirm the correct mobile number is entered. "
            "6. Try alternate OTP delivery methods (call, email) if offered. "
            "7. Check if your SMS inbox is full (delete old messages). "
            "8. If using dual SIM, ensure the correct SIM is set as default for SMS."
        ),
        "category": "sim_esim",
    },
    {
        "title": "KYC Verification for Telecom SIM",
        "text": (
            "All SIM cards in India require KYC (Know Your Customer) verification. "
            "Acceptable KYC documents: Aadhaar card (preferred — supports OTP-based eKYC), "
            "Passport, Voter ID, Driving License, or any government-issued photo ID. "
            "eKYC via Aadhaar OTP is the fastest — no need to visit a store. "
            "Physical KYC requires visiting a carrier store with original documents. "
            "Without completed KYC, your SIM will be deactivated within 30 days. "
            "Incomplete KYC SIMs can only receive calls, not make them."
        ),
        "category": "sim_esim",
    },
]

# ─────────────────────────────────────────────────────────────
#  CATEGORY 6 : IVR / Complaint Resolution  (40 passages)
# ─────────────────────────────────────────────────────────────
IVR_PASSAGES = [
    {
        "title": "Carrier Customer Care Numbers",
        "text": (
            "Customer care helpline numbers for major Indian carriers: "
            "Jio: 199 (from Jio number), 1800 889 9999 (toll-free from any number). "
            "Airtel: 121 (from Airtel), 198 (complaints), 1800 103 4444 (toll-free). "
            "Vi (Vodafone Idea): 111 (from Vi), 172 (complaints from Vi), 9400472111. "
            "BSNL: 1503 or 1800 180 1503 (toll-free). "
            "MTNL: 1503 (Mumbai/Delhi). "
            "Calls to these numbers are free from the respective carrier's SIM. "
            "Hours: 24/7 for critical issues, limited hours for billing queries."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "TRAI Complaint Process",
        "text": (
            "TRAI (Telecom Regulatory Authority of India) handles unresolved telecom "
            "complaints. If your carrier has not resolved your complaint in 30 days: "
            "1. Escalate to the Appellate Authority (details on carrier website). "
            "2. If unresolved in 3 months, file at TRAI's Consumer Complaint Centre. "
            "3. Use the CGPDTM (Centralized Grievance Portal for Digital Telecom Matters). "
            "4. TRAI Helpline: 1800 110 999 (toll-free). "
            "5. Complaints can also be filed at consumerforum.gov.in for service deficiency."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "How to Escalate a Telecom Complaint",
        "text": (
            "Escalation process for unresolved telecom complaints: "
            "Level 1: Contact customer care and get a docket/complaint number. Keep it. "
            "Level 2: If not resolved in 7 days, ask to escalate to Nodal Officer. "
            "Level 3: If not resolved in 30 days, escalate to Appellate Authority. "
            "Level 4: File complaint with TRAI or Consumer Forum. "
            "Always note docket numbers, date/time of calls, and agent names. "
            "Written complaints (email/letter) create a stronger paper trail than calls."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "Getting a Service Request Docket Number",
        "text": (
            "Whenever you raise an issue with customer care, insist on a docket number "
            "(also called complaint ID, ticket number, or reference number). "
            "This is your proof that the complaint was registered. "
            "Write it down immediately — it is used for follow-ups and escalations. "
            "Each carrier uses a different format: Jio uses SR numbers, Airtel uses "
            "ticket IDs, Vi uses complaint reference numbers. "
            "A docket number means the carrier is legally required to resolve within "
            "the prescribed TAT (Turnaround Time) defined by TRAI."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "Call Drop Complaint — How to Report",
        "text": (
            "If you experience frequent call drops in a specific location: "
            "1. Note the location, date, time, and frequency of drops. "
            "2. Report via carrier app: Network > Report Issue > Call Drops. "
            "3. Call customer care and request a network survey at your location. "
            "4. Under TRAI regulations, call drop rate must be below 2% — higher rates "
            "are a compliance violation. "
            "5. If multiple people in your area are affected, a collective complaint "
            "carries more weight. "
            "6. TRAI's MyCall app also allows reporting call quality issues directly."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "Network Outage — What to Do",
        "text": (
            "During a network outage: "
            "1. Check if the issue is local (your area only) or widespread. "
            "2. Visit the carrier's Twitter/X handle for outage announcements. "
            "3. Check downdetector.in for crowd-sourced outage reports. "
            "4. If widespread, wait — outages are usually resolved within 2-6 hours. "
            "5. If only your area is affected, report to customer care for a local "
            "network fault investigation. "
            "6. In emergencies, use Wi-Fi Calling or a different carrier's SIM. "
            "7. After outage resolution, toggle Airplane Mode to reconnect quickly."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "IVR Navigation Tips — Reach a Human Agent Faster",
        "text": (
            "To bypass IVR and reach a human agent quickly: "
            "Jio: Dial 199 > press 9 for other options > press 0 for agent. "
            "Airtel: Dial 121 > press 5 for other queries > press 0 or say 'agent'. "
            "Vi: Dial 111 > press 9 > 0 for representative. "
            "General tip: Stay silent on IVR for 10-15 seconds — many systems transfer "
            "to an agent after repeated silence. "
            "Saying 'representative', 'agent', or 'speak to a person' works on "
            "voice-recognition IVR systems."
        ),
        "category": "ivr_complaints",
    },
    {
        "title": "Email Complaint to Carrier — Template",
        "text": (
            "When sending an email complaint to your telecom carrier: "
            "Airtel: appellate.airtel@in.airtel.com "
            "Jio: jpappellate@jio.com "
            "Vi: appellate@vodafoneidea.com "
            "Include in your email: Your mobile number, account holder name, docket "
            "number from previous complaint, detailed description of the issue, what "
            "resolution you expect, and your preferred contact time. "
            "Written email creates a legal record and triggers stricter resolution timelines."
        ),
        "category": "ivr_complaints",
    },
]


# ─────────────────────────────────────────────────────────────
#  SUPPLEMENTAL PASSAGES — cross-category / general  (40 passages)
# ─────────────────────────────────────────────────────────────
GENERAL_PASSAGES = [
    {
        "title": "Telecom Terms Glossary",
        "text": (
            "Key telecom terms: "
            "APN — Access Point Name, gateway for data connectivity. "
            "VoLTE — Voice over LTE, HD calls over 4G. "
            "MNP — Mobile Number Portability, keep your number when switching carriers. "
            "ISD — International Subscriber Dialing, international calls. "
            "UPC — Unique Porting Code, needed to port your number. "
            "IMEI — International Mobile Equipment Identity, unique device ID. "
            "DND — Do Not Disturb, blocks promotional calls/SMS. "
            "VAS — Value Added Services, extra paid features like caller tunes. "
            "CDR — Call Detail Record, log of all your calls and data usage. "
            "TAT — Turnaround Time, time allowed to resolve complaints."
        ),
        "category": "general",
    },
    {
        "title": "How to File a Complaint on TRAI Portal",
        "text": (
            "To file a telecom complaint directly with TRAI: "
            "1. Visit trai.gov.in > Consumer Corner > Complaint Registration. "
            "2. Or use the CGPDTM portal at cgpdtm.trai.gov.in. "
            "3. Select your carrier and complaint category. "
            "4. Provide your mobile number, complaint details, and previous docket number. "
            "5. Upload supporting documents (bill screenshots, SMS records). "
            "6. You will receive an acknowledgement number. "
            "7. TRAI will forward the complaint to the carrier's Nodal Officer for resolution."
        ),
        "category": "general",
    },
    {
        "title": "Wi-Fi vs Mobile Data — When to Use Which",
        "text": (
            "Use Wi-Fi for: high-bandwidth activities (streaming, downloads), when abroad "
            "to avoid roaming charges, file uploads to cloud storage. "
            "Use Mobile Data for: when moving between locations, in areas without trusted "
            "Wi-Fi, for banking/security-sensitive apps (Wi-Fi can be intercepted). "
            "Best practice: Use both — Wi-Fi for data, keep mobile data as backup. "
            "Enable 'Switch to Mobile Data' in settings to automatically use mobile "
            "data when Wi-Fi is weak. "
            "Avoid using public Wi-Fi for banking apps — use mobile data instead."
        ),
        "category": "general",
    },
    {
        "title": "How to Use *121# USSD for Airtel Services",
        "text": (
            "Airtel USSD codes for quick self-service: "
            "*121# — Main menu (balance, plans, offers). "
            "*121*1# — Check balance and validity. "
            "*121*2# — Data balance check. "
            "*121*8# — Best offer for you. "
            "*121*5# — Value Added Services management. "
            "*141# — Emergency talktime. "
            "*555# — Activate/deactivate caller tune. "
            "*321# — Airtel Wi-Fi calling. "
            "USSD codes work on 2G/3G/4G and do not consume data. "
            "USSD sessions time out after 3 minutes of inactivity."
        ),
        "category": "general",
    },
    {
        "title": "Jio USSD Codes — Self-Service",
        "text": (
            "Jio USSD codes for self-service: "
            "*333# — Main Jio services menu. "
            "*333*1# — Check balance and plan validity. "
            "*333*2# — Data balance. "
            "*333*3# — Best recharge offer. "
            "*333*4# — Buy add-on data pack. "
            "*333*6# — SMS balance. "
            "*333*7# — VAS management. "
            "Note: Jio is primarily a 4G/5G network. USSD codes require 4G signal. "
            "For detailed account management, the MyJio app is recommended."
        ),
        "category": "general",
    },
    {
        "title": "How to Enable DND — Do Not Disturb",
        "text": (
            "To register for DND (Do Not Disturb) and stop promotional calls and SMS: "
            "1. SMS START DND or START 0 to 1909. "
            "2. Or call 1909 and follow the IVR. "
            "3. Or register at ndnc.net.in. "
            "DND has two levels: Fully blocked (no promotional calls/SMS) or "
            "partially blocked (block specific categories). "
            "DND takes 7 days to become effective after registration. "
            "Transactional SMS (OTPs, bank alerts) are NOT blocked by DND. "
            "If DND is active but you still receive promotional calls, report at 1909."
        ),
        "category": "general",
    },
    {
        "title": "Phone Not Making Calls — Troubleshooting Checklist",
        "text": (
            "If you cannot make calls: "
            "1. Check signal — at least 1-2 bars needed for calls. "
            "2. Confirm you are not in Airplane Mode. "
            "3. Check talktime balance (prepaid) or bill status (postpaid). "
            "4. Dial emergency number 112 — if this works, your SIM is active. "
            "5. Check if call barring is enabled: Settings > Call > Additional Settings. "
            "6. Ensure the number you are dialing is not blocked in your phone contacts. "
            "7. Check if a call spending limit is set in postpaid settings. "
            "8. Restart the phone. If issue persists, visit a carrier store."
        ),
        "category": "general",
    },
]


# ─────────────────────────────────────────────────────────────
#  ASSEMBLY
# ─────────────────────────────────────────────────────────────

ALL_PASSAGE_GROUPS = [
    CONNECTIVITY_PASSAGES,
    APN_PASSAGES,
    BILLING_PASSAGES,
    ROAMING_PASSAGES,
    SIM_PASSAGES,
    IVR_PASSAGES,
    GENERAL_PASSAGES,
    VI_FAQ_DATA,
    AIRTEL_FAQ_DATA,
    JIO_FAQ_DATA,
    BSNL_CHARTER_PASSAGES,
    TRAI_PASSGES,
    NEW_GENERAL_PASSAGES
    
]


def build_corpus(output_dir: str = "../../data/raw/telecom_kb") -> list[dict]:
    """
    Assembles all passages, assigns IDs, adds metadata, and saves to JSONL.
    Returns the full list of passage dicts.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    passages = []
    passage_id = 1

    for group in ALL_PASSAGE_GROUPS:
        for p in group:
            passage = {
                "id":       f"tc_{passage_id:04d}",
                "title":    p["title"],
                "text":     p["text"].strip(),
                "category": p["category"],
                "domain":   "telecom",
                "source":   "corpus_builder_v1",
                # Optional: split hint for chunking downstream
                "char_count": len(p["text"].strip()),
            }
            passages.append(passage)
            passage_id += 1

    out_file = out / "passages.jsonl"
    with open(out_file, "w", encoding="utf-8") as f:
        for p in passages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    _print_summary(passages, out_file)
    return passages


def _print_summary(passages: list[dict], out_file: Path) -> None:
    from collections import Counter
    cats = Counter(p["category"] for p in passages)

    print("\n" + "=" * 52)
    print(" Telecom KB Corpus — Build Summary")
    print("=" * 52)
    print(f" Total passages : {len(passages)}")
    print(f" Output file    : {out_file}")
    print("-" * 52)
    print(" Passages per category:")
    for cat, count in sorted(cats.items()):
        bar = "█" * (count // 2)
        print(f"  {cat:<30} {count:>3}  {bar}")
    print("=" * 52)
    print(" Next: python training_data_builder.py")
    print("=" * 52 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build telecom KB corpus")
    parser.add_argument(
        "--output_dir",
        default="../../data/raw/telecom_kb",
        help="Directory to save passages.jsonl"
    )
    args = parser.parse_args()

    build_corpus(args.output_dir)