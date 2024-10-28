document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[id^="{\"type\":\"button\""]').forEach(function(button) {
        button.addEventListener('mouseenter', function() {
            var event = new CustomEvent('hover', { detail: { id: button.id } });
            document.dispatchEvent(event);
        });
    });
});