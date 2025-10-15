// Antique Detail Page JavaScript

document.addEventListener("DOMContentLoaded", () => {
    // Image Gallery Functionality
    initializeImageGallery();
    
    // Wishlist Functionality
    initializeWishlist();
    
    // Keyboard Navigation
    initializeKeyboardNavigation();
});

// Image Gallery
function initializeImageGallery() {
    const mainImage = document.getElementById("mainCarouselImage");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const currentIndexDisplay = document.getElementById("currentIndex");
    const thumbnails = document.querySelectorAll(".thumbnail-wrapper");
    
    if (!mainImage || thumbnails.length === 0) return;
    
    // Get all image URLs
    const images = Array.from(thumbnails).map(thumb => {
        return thumb.querySelector("img").src;
    });
    
    let currentIndex = 0;
    
    // Update image with smooth transition
    function updateImage(index) {
        if (index < 0 || index >= images.length) return;
        
        currentIndex = index;
        
        // Fade out
        mainImage.style.opacity = "0";
        
        setTimeout(() => {
            mainImage.src = images[currentIndex];
            mainImage.style.opacity = "1";
            
            // Update counter
            if (currentIndexDisplay) {
                currentIndexDisplay.textContent = currentIndex + 1;
            }
            
            // Update active thumbnail
            thumbnails.forEach((thumb, idx) => {
                thumb.classList.toggle("active", idx === currentIndex);
            });
            
            // Update button states
            if (prevBtn) {
                prevBtn.disabled = currentIndex === 0;
            }
            if (nextBtn) {
                nextBtn.disabled = currentIndex === images.length - 1;
            }
        }, 300);
    }
    
    // Navigation buttons
    if (prevBtn) {
        prevBtn.addEventListener("click", () => {
            if (currentIndex > 0) {
                updateImage(currentIndex - 1);
            }
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener("click", () => {
            if (currentIndex < images.length - 1) {
                updateImage(currentIndex + 1);
            }
        });
    }
    
    // Thumbnail clicks
    thumbnails.forEach((thumb, index) => {
        thumb.addEventListener("click", () => {
            updateImage(index);
        });
    });
    
    // Initialize button states
    if (prevBtn) prevBtn.disabled = true;
    if (nextBtn && images.length <= 1) nextBtn.disabled = true;
}

// Wishlist Functionality
function initializeWishlist() {
    const wishlistBtn = document.querySelector(".wishlist-btn");
    const wishlistModal = document.getElementById("wishlistModal");
    const modalAntiqueId = document.getElementById("modal-antique-id");
    const wishlistForm = document.getElementById("wishlistForm");
    const wishlistMsg = document.getElementById("wishlist-msg");
    
    if (!wishlistBtn || !wishlistModal) return;
    
    // Bootstrap modal instance
    let modal;
    if (typeof bootstrap !== "undefined") {
        modal = new bootstrap.Modal(wishlistModal);
    }
    
    // Open wishlist modal
    wishlistBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        
        if (modalAntiqueId) {
            modalAntiqueId.value = wishlistBtn.dataset.antiqueId;
        }
        
        if (wishlistMsg) {
            wishlistMsg.innerHTML = "";
        }
        
        if (modal) {
            modal.show();
        }
        
        // Add visual feedback
        wishlistBtn.classList.add("active");
    });
    
    // Handle form submission
    if (wishlistForm) {
        wishlistForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            if (wishlistMsg) {
                wishlistMsg.innerHTML = "";
            }
            
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
                    if (wishlistMsg) {
                        wishlistMsg.innerHTML = '<div class="alert alert-success"><i class="fa-solid fa-check-circle"></i> Added to wishlist successfully!</div>';
                    }
                    
                    // Keep button active
                    wishlistBtn.classList.add("active");
                    
                    setTimeout(() => {
                        if (modal) {
                            modal.hide();
                        }
                    }, 1500);
                } else {
                    if (wishlistMsg) {
                        wishlistMsg.innerHTML = '<div class="alert alert-danger"><i class="fa-solid fa-exclamation-circle"></i> Error adding to wishlist. Please try again.</div>';
                    }
                }
            } catch (error) {
                console.error("Error:", error);
                if (wishlistMsg) {
                    wishlistMsg.innerHTML = '<div class="alert alert-danger"><i class="fa-solid fa-exclamation-circle"></i> Network error. Please check your connection.</div>';
                }
            }
        });
    }
}

// Keyboard Navigation
function initializeKeyboardNavigation() {
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    
    if (!prevBtn || !nextBtn) return;
    
    document.addEventListener("keydown", (e) => {
        // Don't interfere if user is typing in an input
        if (e.target.matches("input, textarea, select")) return;
        
        if (e.key === "ArrowLeft" && !prevBtn.disabled) {
            prevBtn.click();
        } else if (e.key === "ArrowRight" && !nextBtn.disabled) {
            nextBtn.click();
        }
    });
}

// Share functionality (optional enhancement)
function initializeShare() {
    const shareBtn = document.querySelector(".btn-secondary");
    
    if (!shareBtn) return;
    
    shareBtn.addEventListener("click", async () => {
        const title = document.querySelector(".detail-title")?.textContent || "Check out this antique";
        const url = window.location.href;
        
        if (navigator.share) {
            try {
                await navigator.share({
                    title: title,
                    url: url
                });
            } catch (error) {
                console.log("Share cancelled or failed:", error);
            }
        } else {
            // Fallback: copy to clipboard
            try {
                await navigator.clipboard.writeText(url);
                
                // Show feedback
                const originalText = shareBtn.innerHTML;
                shareBtn.innerHTML = '<i class="fa-solid fa-check"></i> Link Copied!';
                shareBtn.disabled = true;
                
                setTimeout(() => {
                    shareBtn.innerHTML = originalText;
                    shareBtn.disabled = false;
                }, 2000);
            } catch (error) {
                console.error("Failed to copy:", error);
            }
        }
    });
}

// Initialize share on load
document.addEventListener("DOMContentLoaded", () => {
    initializeShare();
});