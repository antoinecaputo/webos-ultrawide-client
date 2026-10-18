/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

(function () {
    'use strict';

    var displayMode = 'auto';
    var zoom = 1;
    var statusTimer;

    function syncVideoFit(video) {
        if (!video.matches('.videoPlayerContainer video.htmlvideoplayer')) {
            return;
        }

        var requested = video.style.getPropertyValue('object-fit');
        var fit = requested === 'cover' || requested === 'fill' ? requested : 'contain';
        if (video.getAttribute('data-ultrawide-fit') !== fit) {
            video.setAttribute('data-ultrawide-fit', fit);
        }
    }

    function scanVideos(root) {
        if (root.nodeType !== 1) {
            return;
        }
        if (root.matches('video.htmlvideoplayer')) {
            syncVideoFit(root);
        }
        var videos = root.querySelectorAll('.videoPlayerContainer video.htmlvideoplayer');
        for (var i = 0; i < videos.length; i++) {
            syncVideoFit(videos[i]);
        }
    }

    function playerIsVisible() {
        var video = document.querySelector('.videoPlayerContainer video.htmlvideoplayer');
        if (!video || (!video.currentSrc && !video.readyState)) {
            return false;
        }

        var container = video.parentElement;
        var bounds = container.getBoundingClientRect();
        return bounds.width >= window.innerWidth * 0.75 &&
            bounds.height >= window.innerHeight * 0.75 &&
            window.getComputedStyle(container).display !== 'none';
    }

    function applyDisplayMode() {
        document.body.classList.toggle('ultrawide-cover', displayMode === 'cover');
        document.body.classList.toggle('ultrawide-contain', displayMode === 'contain');
        document.body.classList.toggle('ultrawide-zoomed', zoom !== 1);
        document.body.style.setProperty('--ultrawide-zoom', zoom.toFixed(2));
    }

    function showStatus() {
        var status = document.getElementById('ultrawide-status');
        if (!status) {
            status = document.createElement('div');
            status.id = 'ultrawide-status';
            document.body.appendChild(status);
        }
        var label = displayMode === 'cover' ? 'Plein écran' :
            displayMode === 'contain' ? 'Image entière' : 'Mode Jellyfin';
        status.textContent = label +
            ' · Zoom ' + Math.round(zoom * 100) + ' %';
        status.classList.add('visible');
        clearTimeout(statusTimer);
        statusTimer = setTimeout(function () {
            status.classList.remove('visible');
        }, 1800);
    }

    document.addEventListener('keydown', function (event) {
        if (!playerIsVisible()) {
            return;
        }

        switch (event.keyCode) {
            case 403: // Rouge : Jellyfin / cover / contain
                displayMode = displayMode === 'auto' ? 'cover' :
                    displayMode === 'cover' ? 'contain' : 'auto';
                break;
            case 404: // Vert : zoom arrière
                zoom = Math.max(1, Math.round((zoom - 0.05) * 100) / 100);
                break;
            case 405: // Jaune : zoom avant
                zoom = Math.min(2, Math.round((zoom + 0.05) * 100) / 100);
                break;
            case 406: // Bleu : remettre le zoom à 100 %
                zoom = 1;
                break;
            default:
                return;
        }

        event.preventDefault();
        event.stopImmediatePropagation();
        applyDisplayMode();
        showStatus();
    }, true);

    var observer = new MutationObserver(function (mutations) {
        for (var i = 0; i < mutations.length; i++) {
            var mutation = mutations[i];
            if (mutation.type === 'attributes') {
                syncVideoFit(mutation.target);
            } else {
                for (var j = 0; j < mutation.addedNodes.length; j++) {
                    scanVideos(mutation.addedNodes[j]);
                }
            }
        }
    });
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style']
    });
    scanVideos(document.body);

    applyDisplayMode();
})();
