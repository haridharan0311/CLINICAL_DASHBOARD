export const generateAISuggestion = (alertType, triggerMetric) => {
    if (alertType.includes("Spike") || alertType.includes("Outbreak")) {
        if (triggerMetric.toLowerCase().includes("vector")) return "Urgent: Dispatch municipal fogging team to 5km radius.";
        if (triggerMetric.toLowerCase().includes("gastro")) return "Alert local water authority for contamination check.";
        return "Suggest masking protocols and isolation wards readiness.";
    }
    if (alertType.includes("Stock")) {
        return "AI Triggered: Auto-generate PO to primary vendor for next-day delivery.";
    }
    return "Monitor closely for 24 hours.";
};