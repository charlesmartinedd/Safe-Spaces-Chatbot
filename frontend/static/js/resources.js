/**
 * Resources Page JavaScript
 * Handles resource loading, search, filtering, and pagination
 */

// State
let allResources = [];
let filteredResources = [];
let currentPage = 1;
const resourcesPerPage = 12;

// DOM Elements
const searchInput = document.getElementById('search-input');
const categoryFilter = document.getElementById('category-filter');
const clearFiltersBtn = document.getElementById('clear-filters');
const resourcesGrid = document.getElementById('resources-grid');
const resultsText = document.getElementById('results-text');
const paginationSection = document.getElementById('pagination');
const pageInfo = document.getElementById('page-info');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const pageNumbers = document.getElementById('page-numbers');

// Load resources on page load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize language
    initializeLanguage();

    // Language toggle buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => switchLanguage(btn.dataset.lang));
    });

    loadResources();

    // Event listeners
    searchInput.addEventListener('input', debounce(handleSearch, 300));
    categoryFilter.addEventListener('change', handleFilter);
    clearFiltersBtn.addEventListener('click', clearFilters);
    prevBtn.addEventListener('click', () => goToPage(currentPage - 1));
    nextBtn.addEventListener('click', () => goToPage(currentPage + 1));
});

// Initialize language on page load
function initializeLanguage() {
    const currentLang = langManager.getLanguage();
    updateUI(currentLang);
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === currentLang);
    });
}

// Switch language
function switchLanguage(lang) {
    // Save language preference and refresh page
    langManager.setLanguage(lang);
    location.reload();
}

// Update UI with translations
function updateUI(lang) {
    // Update title
    document.querySelector('h1').textContent = langManager.t('resourcesTitle');

    // Update navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks[0].textContent = '💬 ' + langManager.t('chatLink');
    navLinks[1].textContent = '📚 ' + langManager.t('resourcesNavLink');

    // Update search placeholder
    searchInput.placeholder = langManager.t('searchPlaceholder');

    // Update category filter options
    const categoryOptions = categoryFilter.querySelectorAll('option');
    categoryOptions[0].textContent = langManager.t('categoryAll');
    categoryOptions[1].textContent = langManager.t('categoryOfficial');
    categoryOptions[2].textContent = langManager.t('categoryTrauma');
    categoryOptions[3].textContent = langManager.t('categoryResearch');
    categoryOptions[4].textContent = langManager.t('categoryTools');
    categoryOptions[5].textContent = langManager.t('categoryCommunity');

    // Update clear button
    clearFiltersBtn.textContent = langManager.t('clearFilters');

    // Update pagination buttons
    if (prevBtn) prevBtn.textContent = langManager.t('previous');
    if (nextBtn) nextBtn.textContent = langManager.t('next');

    // Re-render resources with translated text
    if (allResources.length > 0) {
        renderResources();
        updateResultsCount();
    }
}

/**
 * Load resources from JSON file
 */
async function loadResources() {
    try {
        const response = await fetch('/static/data/resources-web.json');
        const data = await response.json();
        allResources = data.resources;
        filteredResources = [...allResources];
        renderResources();
        updateResultsCount();
    } catch (error) {
        console.error('Error loading resources:', error);
        showError('Failed to load resources. Please refresh the page.');
    }
}

/**
 * Get category CSS class for styling
 */
function getCategoryClass(category) {
    const categoryMap = {
        'Official Resources': 'official',
        'Trauma-Informed Education': 'trauma',
        'Research & Evidence': 'research',
        'Practical Tools': 'tools',
        'Community Resources': 'community'
    };
    return categoryMap[category] || 'official';
}

/**
 * Get resource type icon
 */
function getResourceIcon(type) {
    const iconMap = {
        'Training': '🎓',
        'Guide': '📖',
        'Assessment': '📋',
        'Tool': '🛠️',
        'Network': '🤝',
        'Article': '📄'
    };
    return iconMap[type] || '📄';
}

/**
 * Get translated resource type
 */
function getResourceTypeText(type) {
    const typeMap = {
        'Training': langManager.t('typeTraining'),
        'Guide': langManager.t('typeGuide'),
        'Assessment': langManager.t('typeAssessment'),
        'Tool': langManager.t('typeTool'),
        'Network': langManager.t('typeNetwork'),
        'Article': langManager.t('typeArticle')
    };
    return typeMap[type] || type;
}

/**
 * Handle search input
 */
function handleSearch(event) {
    const query = event.target.value.toLowerCase().trim();
    const category = categoryFilter.value;

    filteredResources = allResources.filter(resource => {
        const matchesSearch = !query ||
            resource.title.toLowerCase().includes(query) ||
            resource.description.toLowerCase().includes(query) ||
            resource.keywords.some(k => k.toLowerCase().includes(query));

        const matchesCategory = category === 'all' || resource.category === category;

        return matchesSearch && matchesCategory;
    });

    currentPage = 1;
    renderResources();
    updateResultsCount();
}

/**
 * Handle category filter
 */
function handleFilter() {
    const query = searchInput.value.toLowerCase().trim();
    const category = categoryFilter.value;

    filteredResources = allResources.filter(resource => {
        const matchesSearch = !query ||
            resource.title.toLowerCase().includes(query) ||
            resource.description.toLowerCase().includes(query) ||
            resource.keywords.some(k => k.toLowerCase().includes(query));

        const matchesCategory = category === 'all' || resource.category === category;

        return matchesSearch && matchesCategory;
    });

    currentPage = 1;
    renderResources();
    updateResultsCount();
}

/**
 * Clear all filters
 */
function clearFilters() {
    searchInput.value = '';
    categoryFilter.value = 'all';
    filteredResources = [...allResources];
    currentPage = 1;
    renderResources();
    updateResultsCount();
}

/**
 * Render resources with pagination
 */
function renderResources() {
    const startIndex = (currentPage - 1) * resourcesPerPage;
    const endIndex = startIndex + resourcesPerPage;
    const paginatedResources = filteredResources.slice(startIndex, endIndex);

    if (paginatedResources.length === 0) {
        showEmptyState();
        paginationSection.style.display = 'none';
        return;
    }

    resourcesGrid.innerHTML = paginatedResources.map(resource => createResourceCard(resource)).join('');

    // Show pagination
    paginationSection.style.display = 'flex';
    updatePagination();
}

/**
 * Create HTML for a resource card
 */
function createResourceCard(resource) {
    const categoryClass = getCategoryClass(resource.category);
    const resourceIcon = getResourceIcon(resource.resourceType);
    const hasUrl = resource.url && resource.url.trim() !== '';

    // Create grade level badges
    const gradeBadges = resource.gradeLevels.map(level =>
        `<span class="grade-badge">${escapeHtml(level)}</span>`
    ).join('');

    // Get language-specific content
    const currentLang = langManager.getLanguage();
    const title = currentLang === 'es' && resource.title_es ? resource.title_es : resource.title;
    const description = currentLang === 'es' && resource.description_es ? resource.description_es : resource.description;

    return `
        <div class="resource-card ${categoryClass}">
            <div class="resource-header">
                <h3 class="resource-title">${escapeHtml(title)}</h3>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <span class="resource-type">${getResourceTypeText(resource.resourceType)}</span>
                </div>
            </div>

            <span class="resource-category ${categoryClass}">${escapeHtml(resource.category)}</span>

            <p class="resource-description">${escapeHtml(description)}</p>

            <div class="grade-levels">
                ${gradeBadges}
                ${resource.location ? `<span class="location-badge">${resource.location === 'California' ? langManager.t('locationCalifornia') : langManager.t('locationNational')}</span>` : ''}
            </div>

            <div class="resource-footer">
                ${hasUrl ?
                    `<a href="${escapeHtml(resource.url)}" class="resource-link" target="_blank" rel="noopener">
                        ${langManager.t('visitResource')}
                    </a>` :
                    `<span class="resource-link">${langManager.t('viewDetails')}</span>`
                }
            </div>
        </div>
    `;
}

// Removed handleResourceClick - cards now only clickable via button

/**
 * Update pagination controls
 */
function updatePagination() {
    const totalPages = Math.ceil(filteredResources.length / resourcesPerPage);
    const startIndex = (currentPage - 1) * resourcesPerPage + 1;
    const endIndex = Math.min(currentPage * resourcesPerPage, filteredResources.length);

    // Update page info
    pageInfo.textContent = `${langManager.t('showingText')} ${startIndex}-${endIndex} ${langManager.t('ofText')} ${filteredResources.length}`;

    // Update buttons
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;

    // Generate page numbers (show max 5 pages)
    const maxPages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPages / 2));
    let endPage = Math.min(totalPages, startPage + maxPages - 1);

    if (endPage - startPage < maxPages - 1) {
        startPage = Math.max(1, endPage - maxPages + 1);
    }

    const pageNumbersHTML = [];
    for (let i = startPage; i <= endPage; i++) {
        pageNumbersHTML.push(`
            <button
                class="page-number ${i === currentPage ? 'active' : ''}"
                onclick="goToPage(${i})"
            >
                ${i}
            </button>
        `);
    }

    pageNumbers.innerHTML = pageNumbersHTML.join('');
}

/**
 * Go to specific page
 */
function goToPage(page) {
    const totalPages = Math.ceil(filteredResources.length / resourcesPerPage);
    if (page < 1 || page > totalPages) return;

    currentPage = page;
    renderResources();

    // Scroll to top of resources
    resourcesGrid.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Update results count text
 */
function updateResultsCount() {
    const count = filteredResources.length;
    const total = allResources.length;

    if (count === total) {
        resultsText.textContent = `${count} ${langManager.t('resourcesAvailable')}`;
    } else {
        resultsText.textContent = `${count} ${langManager.t('ofText')} ${total} ${langManager.t('resourcesFound')}`;
    }
}

/**
 * Show empty state
 */
function showEmptyState() {
    resourcesGrid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
            <h3>${langManager.t('noResourcesTitle')}</h3>
            <p>${langManager.t('noResourcesText')}</p>
        </div>
    `;
}

/**
 * Show error message
 */
function showError(message) {
    resourcesGrid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
            <h3>Error</h3>
            <p>${escapeHtml(message)}</p>
        </div>
    `;
}

/**
 * Debounce function for search input
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Truncate text to specified length
 */
function truncate(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
