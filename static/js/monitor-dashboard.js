// Configuration
const CONFIG = {
    autoRefreshInterval: 30000, // 30 seconds
    endpoints: {
        addUrl: "/api/urls/",
        checkNow: "/api/urls/",
        deleteUrl: "/api/urls/",
        history: "/api/urls/"
    }
};

// State management
let autoRefreshTimer = null;

// jQuery setup for CSRF token
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
        }
    }
});

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// Initialize on a page load
$(document).ready(function() {
    initializeEventListeners();
    initializeSemanticUI();
    startAutoRefresh();
});

function initializeSemanticUI() {
    // Initialize form validation
    $('.ui.form').form({
        fields: {
            name: {
                identifier: 'name',
                rules: [{
                    type: 'empty',
                    prompt: 'Please enter a name for the URL'
                }]
            },
            url: {
                identifier: 'url',
                rules: [{
                    type: 'empty',
                    prompt: 'Please enter a URL'
                }, {
                    type: 'url',
                    prompt: 'Please enter a valid URL'
                }]
            }
        }
    });

    // Initialize modal
    $('#historyModal').modal({
        closable: true,
        blurring: true
    });
}

function initializeEventListeners() {
    // Add URL form handler
    $('#addUrlForm').on('submit', handleAddUrl);
}

// Enhanced form submission with Semantic UI integration
function handleAddUrl(e) {
    e.preventDefault();

    const $form = $('#addUrlForm');
    const $submitBtn = $('#addUrlBtn');
    const $nameInput = $('#name');
    const $urlInput = $('#url');

    // Clear previous errors
    clearFormErrors();

    // Client-side validation using Semantic UI
    if (!$form.form('is valid')) {
        return;
    }

    // Show loading state
    setButtonLoading($submitBtn, true);

    const data = {
        name: $nameInput.val(),
        url: $urlInput.val()
    };

    $.ajax({
        url: CONFIG.endpoints.addUrl,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function() {
            showToast('URL added successfully!', 'success');
            $form.form('reset');
            refreshUrlGrid();
        },
        error: function(xhr) {
            console.error('Error adding URL:', xhr);

            if (xhr.responseJSON) {
                const result = xhr.responseJSON;
                // Handle validation errors
                if (result.name || result.url) {
                    if (result.name) showFieldError('name', result.name[0]);
                    if (result.url) showFieldError('url', result.url[0]);
                } else {
                    showToast('Error adding URL', 'error');
                }
            } else {
                showToast('Network error. Please try again.', 'error');
            }
        },
        complete: function() {
            setButtonLoading($submitBtn, false);
        }
    });
}

// Enhanced check now with Semantic UI feedback
function checkNow(urlId) {
    const $card = $(`[data-url-id="${urlId}"]`);
    const $button = $card.find('.ui.teal.button');

    setButtonLoading($button, true);
    $card.addClass('updating');

    $.ajax({
        url: `${CONFIG.endpoints.checkNow}${urlId}/check-now/`,
        type: 'POST',
        success: function(result) {
            showToast(result.message || 'Health check completed!', 'success');
            setTimeout(() => refreshUrlGrid(), 2000);
        },
        error: function(xhr) {
            console.error('Error checking URL:', xhr);

            const result = xhr.responseJSON;

            if (xhr.status === 503) {
                showToast(
                    (result && result.error) || 'Health check service is temporarily unavailable',
                    'error'
                );
                console.warn('Celery service unavailable:', result);
            } else if (xhr.status === 500) {
                showToast('An internal error occurred. Please try again later.', 'error');
                console.error('Internal server error:', result);
            } else if (xhr.status === 0) {
                showToast('Network error. Please check your connection.', 'error');
            } else {
                showToast((result && result.error) || 'Error checking URL', 'error');
                console.error('Health check error:', result);
            }
        },
        complete: function() {
            setButtonLoading($button, false);
            $card.removeClass('updating');
        }
    });
}

// Enhanced delete with Semantic UI confirmation
function deleteUrl(urlId) {
    // Use Semantic UI modal for confirmation
    $('body').append(`
        <div class="ui small modal" id="deleteConfirmModal">
            <div class="header">
                <i class="warning sign icon"></i>
                Confirm Deletion
            </div>
            <div class="content">
                <p>Are you sure you want to delete this URL? This action cannot be undone.</p>
            </div>
            <div class="actions">
                <div class="ui cancel button">
                    <i class="remove icon"></i>
                    Cancel
                </div>
                <div class="ui red ok button">
                    <i class="checkmark icon"></i>
                    Delete
                </div>
            </div>
        </div>
    `);

    $('#deleteConfirmModal').modal({
        closable: false,
        onApprove: function() {
            performDelete(urlId);
            return true;
        },
        onHidden: function() {
            $(this).remove();
        }
    }).modal('show');
}

function performDelete(urlId) {
    const $card = $(`[data-url-id="${urlId}"]`);
    const $button = $card.find('.ui.red.button');

    setButtonLoading($button, true);

    $.ajax({
        url: `${CONFIG.endpoints.deleteUrl}${urlId}/`,
        type: 'DELETE',
        success: function() {
            showToast('URL deleted successfully', 'success');
            $card.transition('scale out', '300ms', function() {
                $card.remove();
                checkEmptyState();
            });
        },
        error: function(xhr) {
            console.error('Error deleting URL:', xhr);
            if (xhr.status === 0) {
                showToast('Network error during deletion', 'error');
            } else {
                showToast('Error deleting URL', 'error');
            }
            setButtonLoading($button, false);
        }
    });
    // Reload page
    refreshUrlGrid();
}

// Enhanced history view with Semantic UI modal
function viewHistory(urlId) {
    const $modal = $('#historyModal');
    const $content = $('#historyContent');

    // Show modal with a loading state
    $content.html(`
        <div class="ui active centered inline loader"></div>
        <p style="text-align: center; margin-top: 1rem;">Loading history...</p>
    `);

    $modal.modal('show');

    $.ajax({
        url: `${CONFIG.endpoints.history}${urlId}/history/`,
        type: 'GET',
        success: function(result) {
            displayHistory(result);
        },
        error: function(xhr) {
            console.error('Error fetching history:', xhr);
            if (xhr.status === 0) {
                $content.html(`
                    <div class="ui negative message">
                        <div class="header">Network Error</div>
                        <p>Unable to load history due to network issues.</p>
                    </div>
                `);
            } else {
                $content.html(`
                    <div class="ui negative message">
                        <div class="header">Error Loading History</div>
                        <p>An error occurred while loading the health check history.</p>
                    </div>
                `);
            }
        }
    });
}


function displayHistory(result) {
    const $content = $('#historyContent');

    // Handle both array and object formats
    const history = result.history || result;

    if (!history || history.length === 0) {
        $content.html(`
            <div class="ui placeholder segment">
                <div class="ui icon header">
                    <i class="clock outline icon"></i>
                    No health check history available
                </div>
            </div>
        `);
        return;
    }

    // Update the modal title if we have URL info
    if (result.url_name) {
        $('#historyTitle').text(`Health Check History - ${result.url_name}`);
    }

    const historyHTML = `
        <div class="ui divided items">
            ${history.map(check => `
                <div class="item history-item">
                    <div class="content">
                        <div class="header">
                            <i class="clock icon"></i>
                            ${new Date(check.checked_at).toLocaleString()}
                        </div>
                        <div class="meta">
                            <span class="ui small label ${check.is_healthy ? 'green' : 'red'}">
                                Status: ${check.status_code || 'Error'}
                            </span>
                            <span class="ui small label blue">
                                Response: ${(check.response_time || 0).toFixed(3)}s
                            </span>
                            ${check.error_message ? `
                                <div class="ui small label orange">
                                    Error: ${check.error_message}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    <div class="status-icon">
                        ${check.is_healthy ? 
                            '<i class="check circle large green icon"></i>' : 
                            '<i class="times circle large red icon"></i>'
                        }
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    $content.html(historyHTML);
}

function closeHistoryModal() {
    $('#historyModal').modal('hide');
}

// Utility functions adapted for Semantic UI
function clearFormErrors() {
    $('.ui.form').form('remove prompt', ['name', 'url']);
    $('#nameError, #urlError').hide();
}

function showFieldError(fieldName, message) {
    $(`#${fieldName}Error`).text(message).show();
    $('.ui.form').form('add prompt', fieldName, message);
}

function setButtonLoading(button, isLoading) {
    const $button = $(button);

    if (isLoading) {
        $button.addClass('loading disabled');
    } else {
        $button.removeClass('loading disabled');
    }
}

function showToast(message, type = 'info') {
    // Use Semantic UI toast (requires fomantic-ui or custom implementation)
    const iconMap = {
        success: 'check circle',
        error: 'times circle',
        info: 'info circle',
        warning: 'exclamation triangle'
    };

    const colorMap = {
        success: 'green',
        error: 'red',
        info: 'blue',
        warning: 'yellow'
    };

    // Create toast using a Semantic UI message
    const $toast = $(`
        <div class="ui ${colorMap[type]} message floating" style="
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            min-width: 300px;
            transform: translateX(400px);
            transition: transform 0.3s ease;
        ">
            <i class="${iconMap[type]} icon"></i>
            ${message}
            <i class="close icon" onclick="$(this).closest('.message').transition('fly right')"></i>
        </div>
    `);

    $('body').append($toast);

    // Animate in
    setTimeout(() => {
        $toast.css('transform', 'translateX(0)');
    }, 100);

    // Auto remove
    setTimeout(() => {
        $toast.transition('fly right', '300ms', function() {
            $(this).remove();
        });
    }, 4000);
}

function getCSRFToken() {
    return $('[name=csrfmiddlewaretoken]').val() ||
           $('meta[name=csrf-token]').attr('content') ||
           getCookie('csrftoken');
}

// Getting csrf token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function refreshUrlGrid() {
    $.ajax({
        url: window.location.href,
        type: 'GET',
        success: function(html) {
            const $newGrid = $(html).find('#urlGrid');
            if ($newGrid.length) {
                $('#urlGrid').html($newGrid.html());
            }
        },
        error: function(xhr) {
            console.error('Error refreshing grid:', xhr);
        }
    });
}

function checkEmptyState() {
    const $grid = $('#urlGrid');
    const $cards = $grid.find('.ui.card');

    if ($cards.length === 0) {
        $grid.html(`
            <div class="sixteen wide column" id="emptyState">
                <div class="ui placeholder segment">
                    <div class="ui icon header">
                        <i class="search icon"></i>
                        No URLs being monitored yet
                    </div>
                    <div class="ui primary button" onclick="document.getElementById('name').focus()">
                        Add Your First URL
                    </div>
                </div>
            </div>
        `);
    }
}

function startAutoRefresh() {
    autoRefreshTimer = setInterval(() => {
        refreshUrlGrid();
    }, CONFIG.autoRefreshInterval);
}

function stopAutoRefresh() {
    if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
        autoRefreshTimer = null;
    }
}

// Pause auto-refresh when the page is not visible
$(document).on('visibilitychange', function() {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
    }
});

// Clean up on page unload
$(window).on('beforeunload', function() {
    stopAutoRefresh();
});