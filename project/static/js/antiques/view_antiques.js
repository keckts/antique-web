document.addEventListener("DOMContentLoaded", () => {
    const wishlistIcons = document.querySelectorAll(".wishlist-icon");
    const modal = new bootstrap.Modal(document.getElementById("wishlistModal"));
    const modalAntiqueId = document.getElementById("modal-antique-id");
    const wishlistForm = document.getElementById("wishlistForm");
    const wishlistMsg = document.getElementById("wishlist-msg");

    wishlistIcons.forEach(icon => {
        icon.addEventListener("click", () => {
            modalAntiqueId.value = icon.dataset.antiqueId;
            wishlistMsg.innerHTML = "";
            modal.show();
        });
    });

    wishlistForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        wishlistMsg.innerHTML = "";

        const formData = new FormData(wishlistForm);

        const response = await fetch(addToWishlistUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData,
        });

        if (response.ok) {
            wishlistMsg.innerHTML = '<div class="alert alert-success"><i class="fa-solid fa-check-circle"></i> Added to wishlist!</div>';
        } else {
            wishlistMsg.innerHTML = '<div class="alert alert-danger"><i class="fa-solid fa-exclamation-circle"></i> Error adding to wishlist.</div>';
        }
    });
});

// View Antiques JavaScript - Search, Filter, Pagination, and Image Carousel

document.addEventListener("DOMContentLoaded", () => {
    // Elements
    const searchInput = document.getElementById("searchInput");
    const typeFilter = document.getElementById("typeFilter");
    const antiquesGrid = document.getElementById("antiquesGrid");
    const antiqueCards = document.querySelectorAll(".antique-card");
    const resultsCount = document.getElementById("resultsCount");
    const loadMoreBtn = document.getElementById("loadMoreBtn");
    const loadMoreWrapper = document.getElementById("loadMoreWrapper");

    // Pagination settings
    const ITEMS_PER_PAGE = 30;
    let currentPage = 1;
    let filteredCards = Array.from(antiqueCards);

    // Initialize
    updateDisplay();
    initializeCarousels();

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener("input", filterAntiques);
    }

    // Filter functionality
    if (typeFilter) {
        typeFilter.addEventListener("change", filterAntiques);
    }

    // Load more functionality
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener("click", loadMoreAntiques);
    }

    // Filter antiques based on search and type
    function filterAntiques() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : "";
        const selectedType = typeFilter ? typeFilter.value : "";

        filteredCards = Array.from(antiqueCards).filter(card => {
            const title = card.dataset.title || "";
            const description = card.dataset.description || "";
            const type = card.dataset.type || "";

            const matchesSearch = title.includes(searchTerm) || description.includes(searchTerm);
            const matchesType = !selectedType || type === selectedType;

            return matchesSearch && matchesType;
        });

        currentPage = 1;
        updateDisplay();
    }

    // Update display based on current filters and pagination
    function updateDisplay() {
        // Hide all cards first
        antiqueCards.forEach(card => card.classList.add("hidden"));

        // Calculate visible cards
        const startIndex = 0;
        const endIndex = currentPage * ITEMS_PER_PAGE;
        const visibleCards = filteredCards.slice(startIndex, endIndex);

        // Show visible cards
        visibleCards.forEach(card => card.classList.remove("hidden"));

        // Update results count
        if (resultsCount) {
            resultsCount.textContent = filteredCards.length;
        }

        // Show/hide load more button
        if (loadMoreWrapper) {
            if (filteredCards.length > endIndex) {
                loadMoreWrapper.style.display = "block";
            } else {
                loadMoreWrapper.style.display = "none";
            }
        }

        // Scroll to top if filtering (not on initial load)
        if (currentPage === 1 && searchInput && searchInput.value) {
            window.scrollTo({ top: 0, behavior: "smooth" });
        }
    }

    // Load more antiques
    function loadMoreAntiques() {
        currentPage++;
        updateDisplay();

        // Scroll to first newly loaded item
        const newlyVisibleIndex = (currentPage - 1) * ITEMS_PER_PAGE;
        const newCard = filteredCards[newlyVisibleIndex];
        if (newCard) {
            setTimeout(() => {
                newCard.scrollIntoView({ behavior: "smooth", block: "center" });
            }, 100);
        }
    }

    // Wishlist Modal functionality
    const wishlistIcons = document.querySelectorAll(".wishlist-icon");
    const wishlistModal = document.getElementById("wishlistModal");
    const modalAntiqueId = document.getElementById("modal-antique-id");
    const wishlistForm = document.getElementById("wishlistForm");
    const wishlistMsg = document.getElementById("wishlist-msg");

    if (wishlistModal && typeof bootstrap !== "undefined") {
        const modal = new bootstrap.Modal(wishlistModal);

        wishlistIcons.forEach(icon => {
            icon.addEventListener("click", (e) => {
                e.stopPropagation();
                modalAntiqueId.value = icon.dataset.antiqueId;
                wishlistMsg.innerHTML = "";
                modal.show();
            });
        });

        if (wishlistForm) {
            wishlistForm.addEventListener("submit", async (e) => {
                e.preventDefault();
                wishlistMsg.innerHTML = "";

                const formData = new FormData(wishlistForm);

                try {
                    const response = await fetch(wishlistForm.action || window.location.href, {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
                            "X-Requested-With": "XMLHttpRequest",
                        },
                        body: formData,
                    });

                    if (response.ok) {
                        wishlistMsg.innerHTML = '<div class="alert alert-success"><i class="fa-solid fa-check-circle"></i> Added to wishlist!</div>';
                    } else {
                        wishlistMsg.innerHTML = '<div class="alert alert-danger"><i class="fa-solid fa-exclamation-circle"></i> Error adding to wishlist.</div>';
                    }

                    setTimeout(() => {
                        modal.hide();
                    }, 1500);
                } catch (error) {
                    wishlistMsg.innerHTML = '<div class="alert alert-danger"><i class="fa-solid fa-exclamation-circle"></i> Network error.</div>';
                }
            });
        }
    }
});

// Image Carousel Functionality
function initializeCarousels() {
    const carousels = document.querySelectorAll(".image-carousel");
    const autoPlayInterval = 5000; // 5 seconds

    carousels.forEach(carousel => {
        const images = carousel.querySelectorAll(".carousel-image");
        const dots = carousel.querySelectorAll(".dot");

        if (images.length <= 1) return;

        let currentIndex = 0;
        let autoPlayTimer = null;

        // Start auto-play on hover
        carousel.parentElement.addEventListener("mouseenter", () => {
            autoPlayTimer = setInterval(() => {
                showImage(currentIndex + 1);
            }, autoPlayInterval);
        });

        // Stop auto-play when mouse leaves
        carousel.parentElement.addEventListener("mouseleave", () => {
            if (autoPlayTimer) {
                clearInterval(autoPlayTimer);
                autoPlayTimer = null;
            }
        });

        function showImage(index) {
            // Wrap around
            if (index >= images.length) index = 0;
            if (index < 0) index = images.length - 1;

            // Update images
            images[currentIndex].classList.remove("active");
            images[index].classList.add("active");

            // Update dots
            if (dots.length > 0) {
                dots[currentIndex].classList.remove("active");
                dots[index].classList.add("active");
            }

            currentIndex = index;
        }

        // Dot navigation
        dots.forEach((dot, index) => {
            dot.addEventListener("click", (e) => {
                e.stopPropagation();
                showImage(index);
                
                // Reset auto-play timer
                if (autoPlayTimer) {
                    clearInterval(autoPlayTimer);
                    autoPlayTimer = setInterval(() => {
                        showImage(currentIndex + 1);
                    }, autoPlayInterval);
                }
            });
        });

        // Store the showImage function for external access
        carousel.showImage = showImage;
    });
}

// Change image with arrow buttons
function changeImage(button, direction) {
    const carousel = button.closest(".image-carousel");
    const images = carousel.querySelectorAll(".carousel-image");
    let currentIndex = Array.from(images).findIndex(img => img.classList.contains("active"));

    if (carousel.showImage) {
        carousel.showImage(currentIndex + direction);
    }
}