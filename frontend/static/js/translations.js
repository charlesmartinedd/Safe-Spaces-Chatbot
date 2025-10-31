/**
 * Bilingual Translations - English / Spanish
 * RRC Support Coach Application
 */

const translations = {
    en: {
        // Header
        appTitle: "Recognize, Respond, Connect: Support Coach",
        resourcesLink: "Resources",

        // Chat Page
        welcomeTitle: "RRC Support Coach",
        welcomeStrong: "Welcome!",
        welcomeIntro: "I'm your RRC Support Coach.",
        welcomePrompt: "To provide tailored guidance, please share:",
        welcomeQuestion1: "What grade level(s) do you work with?",
        welcomeQuestion2: "What is your role in education?",
        welcomeClosing: "Let me know how I can support you today!",

        // Input
        inputPlaceholder: "Type your question or describe the scenario...",
        sendButton: "Send",

        // Messages
        userLabel: "You",
        coachLabel: "RRC Coach",
        coachBadge: "🎓 RRC Coach",
        sourcesHeader: "Sources Referenced",

        // Error messages
        errorMessage: "Sorry, I encountered an error.",
        errorRetry: "Please try again or refresh the page.",

        // Resources Page
        resourcesTitle: "Recognize, Respond, Connect: Resources",
        chatLink: "Chat with Coach",
        resourcesNavLink: "Resources",
        searchPlaceholder: "🔍 Search resources by keyword or topic...",

        // Categories
        categoryAll: "All Categories",
        categoryOfficial: "🏛️ Official Resources",
        categoryTrauma: "📚 Trauma-Informed Education",
        categoryResearch: "🔬 Research & Evidence",
        categoryTools: "🛠️ Practical Tools",
        categoryCommunity: "🤝 Community Resources",

        // Buttons
        clearFilters: "Clear Filters",
        visitResource: "Visit Resource →",
        viewDetails: "View Details",

        // Pagination
        showingText: "Showing",
        ofText: "of",
        previous: "← Previous",
        next: "Next →",

        // Results
        resourcesAvailable: "resources available",
        resourcesFound: "resources found",
        loadingResources: "Loading resources...",
        noResourcesTitle: "No resources found",
        noResourcesText: "Try adjusting your search or filters",

        // Resource Types
        typeTraining: "🎓 Training",
        typeGuide: "📖 Guide",
        typeAssessment: "📋 Assessment",
        typeTool: "🛠️ Tool",
        typeNetwork: "🤝 Network",
        typeArticle: "📄 Article",

        // Locations
        locationCalifornia: "📍 California",
        locationNational: "📍 National",

        // Language Toggle
        languageLabel: "Language:",
        englishLabel: "English",
        spanishLabel: "Español"
    },
    es: {
        // Header
        appTitle: "Reconocer, Responder, Conectar: Coach de Apoyo",
        resourcesLink: "Recursos",

        // Chat Page
        welcomeTitle: "Coach de Apoyo RRC",
        welcomeStrong: "¡Bienvenido!",
        welcomeIntro: "Soy tu Coach de Apoyo RRC.",
        welcomePrompt: "Para proporcionar orientación personalizada, por favor comparte:",
        welcomeQuestion1: "¿Con qué nivel(es) de grado trabajas?",
        welcomeQuestion2: "¿Cuál es tu rol en la educación?",
        welcomeClosing: "¡Déjame saber cómo puedo apoyarte hoy!",

        // Input
        inputPlaceholder: "Escribe tu pregunta o describe el escenario...",
        sendButton: "Enviar",

        // Messages
        userLabel: "Tú",
        coachLabel: "Coach RRC",
        coachBadge: "🎓 Coach RRC",
        sourcesHeader: "Fuentes Referenciadas",

        // Error messages
        errorMessage: "Lo siento, encontré un error.",
        errorRetry: "Por favor, inténtalo de nuevo o actualiza la página.",

        // Resources Page
        resourcesTitle: "Reconocer, Responder, Conectar: Recursos",
        chatLink: "Chatear con Coach",
        resourcesNavLink: "Recursos",
        searchPlaceholder: "🔍 Buscar recursos por palabra clave o tema...",

        // Categories
        categoryAll: "Todas las Categorías",
        categoryOfficial: "🏛️ Recursos Oficiales",
        categoryTrauma: "📚 Educación Informada sobre Trauma",
        categoryResearch: "🔬 Investigación y Evidencia",
        categoryTools: "🛠️ Herramientas Prácticas",
        categoryCommunity: "🤝 Recursos Comunitarios",

        // Buttons
        clearFilters: "Limpiar Filtros",
        visitResource: "Visitar Recurso →",
        viewDetails: "Ver Detalles",

        // Pagination
        showingText: "Mostrando",
        ofText: "de",
        previous: "← Anterior",
        next: "Siguiente →",

        // Results
        resourcesAvailable: "recursos disponibles",
        resourcesFound: "recursos encontrados",
        loadingResources: "Cargando recursos...",
        noResourcesTitle: "No se encontraron recursos",
        noResourcesText: "Intenta ajustar tu búsqueda o filtros",

        // Resource Types
        typeTraining: "🎓 Capacitación",
        typeGuide: "📖 Guía",
        typeAssessment: "📋 Evaluación",
        typeTool: "🛠️ Herramienta",
        typeNetwork: "🤝 Red",
        typeArticle: "📄 Artículo",

        // Locations
        locationCalifornia: "📍 California",
        locationNational: "📍 Nacional",

        // Language Toggle
        languageLabel: "Idioma:",
        englishLabel: "English",
        spanishLabel: "Español"
    }
};

// Language management
class LanguageManager {
    constructor() {
        this.currentLang = localStorage.getItem('preferredLanguage') || 'en';
    }

    setLanguage(lang) {
        this.currentLang = lang;
        localStorage.setItem('preferredLanguage', lang);
        document.documentElement.lang = lang;
    }

    getLanguage() {
        return this.currentLang;
    }

    t(key) {
        return translations[this.currentLang][key] || translations['en'][key] || key;
    }
}

// Global language manager instance
const langManager = new LanguageManager();
