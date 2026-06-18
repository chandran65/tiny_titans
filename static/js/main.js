// Tiny Titans Tech Academy - Main JavaScript Controller

document.addEventListener('DOMContentLoaded', () => {
    // 1. Header Scroll Styling
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // 2. Mobile Nav Toggle Menu
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        // Close menu when clicking nav links
        const navLinks = document.querySelectorAll('.nav-item a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
    }

    // 3. Homepage Programs Tabs Switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    if (tabBtns.length > 0 && tabContents.length > 0) {
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetTab = btn.getAttribute('data-tab');
                
                // Toggle active buttons
                tabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Toggle active contents
                tabContents.forEach(content => {
                    content.classList.remove('active');
                    if (content.id === targetTab) {
                        content.classList.add('active');
                    }
                });
            });
        });
    }

    // 4. FAQ Accordion Panels
    const faqHeaders = document.querySelectorAll('.faq-header');
    if (faqHeaders.length > 0) {
        faqHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const parent = header.parentElement;
                
                // Close other open panels (optional but clean)
                const openItems = document.querySelectorAll('.faq-item.active');
                openItems.forEach(item => {
                    if (item !== parent) {
                        item.classList.remove('active');
                    }
                });
                
                parent.classList.toggle('active');
            });
        });
    }

    // 5. Gallery Filters and Lightbox
    const filterBtns = document.querySelectorAll('.filter-btn');
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    if (filterBtns.length > 0 && galleryItems.length > 0) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Change active filter tab
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const filterValue = btn.getAttribute('data-filter');
                
                galleryItems.forEach(item => {
                    if (filterValue === 'all' || item.getAttribute('data-category') === filterValue) {
                        item.style.display = 'block';
                        setTimeout(() => { item.style.opacity = '1'; item.style.transform = 'scale(1)'; }, 50);
                    } else {
                        item.style.opacity = '0';
                        item.style.transform = 'scale(0.8)';
                        setTimeout(() => { item.style.display = 'none'; }, 300);
                    }
                });
            });
        });
    }

    // Lightbox Functionality
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxCaption = document.getElementById('lightbox-caption');
    const lightboxClose = document.getElementById('lightbox-close');

    if (galleryItems.length > 0 && lightbox) {
        galleryItems.forEach(item => {
            item.addEventListener('click', () => {
                const img = item.querySelector('img');
                const title = item.querySelector('h4').textContent;
                
                if (img && lightboxImg) {
                    lightboxImg.src = img.src;
                    if (lightboxCaption) lightboxCaption.textContent = title;
                    lightbox.classList.add('active');
                }
            });
        });

        if (lightboxClose) {
            lightboxClose.addEventListener('click', () => {
                lightbox.classList.remove('active');
            });
        }

        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) {
                lightbox.classList.remove('active');
            }
        });
    }

    // 6. Admissions Application Form Handling
    const admissionsForm = document.getElementById('admissionsForm');
    if (admissionsForm) {
        admissionsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = admissionsForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.textContent;
            const messageDiv = document.getElementById('formMessage');
            
            // Collect Form Inputs
            const formData = {
                studentName: document.getElementById('studentName').value,
                parentName: document.getElementById('parentName').value,
                mobileNumber: document.getElementById('mobileNumber').value,
                email: document.getElementById('email').value,
                age: document.getElementById('age').value,
                schoolCollege: document.getElementById('schoolCollege').value,
                interestedProgram: document.getElementById('interestedProgram').value,
                preferredBatch: document.getElementById('preferredBatch').value
            };
            
            // Reset message banner
            messageDiv.className = 'form-message';
            messageDiv.style.display = 'none';
            
            // Simple validation
            if (!formData.studentName || !formData.parentName || !formData.mobileNumber || !formData.email || !formData.age || !formData.schoolCollege || !formData.interestedProgram || !formData.preferredBatch) {
                messageDiv.textContent = "Please fill in all the required fields.";
                messageDiv.classList.add('error');
                return;
            }
            
            try {
                // Set Loading state
                submitBtn.disabled = true;
                submitBtn.textContent = "Submitting Application...";
                
                const response = await fetch('/api/admissions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    messageDiv.textContent = result.message;
                    messageDiv.classList.add('success');
                    admissionsForm.reset();
                } else {
                    messageDiv.textContent = result.message || "An error occurred. Please try again.";
                    messageDiv.classList.add('error');
                }
            } catch (err) {
                console.error("Submission error:", err);
                messageDiv.textContent = "Failed to submit request due to server connection issues. Please try again.";
                messageDiv.classList.add('error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalBtnText;
            }
        });
    }

    // 7. Blog Integration Pages
    const blogsContainer = document.getElementById('blogs-container');
    if (blogsContainer) {
        // Fetch all blogs
        fetch('/api/blog')
            .then(res => res.json())
            .then(data => {
                if (data.success && data.blogs.length > 0) {
                    blogsContainer.innerHTML = '';
                    data.blogs.forEach(post => {
                        const card = document.createElement('div');
                        card.className = 'blog-card';
                        
                        const date = new Date(post.created_at).toLocaleDateString('en-US', {
                            year: 'numeric', month: 'short', day: 'numeric'
                        });
                        
                        card.innerHTML = `
                            <div class="blog-card-img">
                                <img src="${post.image_url || '/images/blog_fallback.png'}" alt="${post.title}">
                            </div>
                            <div class="blog-card-body">
                                <div>
                                    <div class="blog-card-meta">
                                        <span>${post.category}</span>
                                        <span>${date}</span>
                                    </div>
                                    <h3>${post.title}</h3>
                                    <p>${post.summary}</p>
                                </div>
                                <a href="blog-post.html?post=${post.slug}" class="blog-card-link">
                                    Read Article &rarr;
                                </a>
                            </div>
                        `;
                        blogsContainer.appendChild(card);
                    });
                } else {
                    blogsContainer.innerHTML = '<p style="grid-column: span 3; text-align: center; color: var(--text-muted);">No blog posts found. Check back soon!</p>';
                }
            })
            .catch(err => {
                console.error("Error fetching blogs:", err);
                blogsContainer.innerHTML = '<p style="grid-column: span 3; text-align: center; color: red;">Failed to load blogs from server.</p>';
            });
    }

    // Render Single Blog Post Page
    const blogPostContent = document.getElementById('blog-post-content');
    if (blogPostContent) {
        const urlParams = new URLSearchParams(window.location.search);
        const slug = urlParams.get('post');
        
        if (!slug) {
            window.location.href = 'blog.html';
            return;
        }
        
        fetch(`/api/blog/${slug}`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const post = data.blog;
                    const date = new Date(post.created_at).toLocaleDateString('en-US', {
                        year: 'numeric', month: 'long', day: 'numeric'
                    });
                    
                    document.title = `${post.title} | Tiny Titans Tech Academy`;
                    
                    blogPostContent.innerHTML = `
                        <div class="blog-detail-header">
                            <span class="blog-detail-category">${post.category}</span>
                            <h1>${post.title}</h1>
                            <div class="blog-detail-meta">
                                <span><strong>By:</strong> ${post.author || 'Tiny Titans Team'}</span>
                                <span><strong>Published:</strong> ${date}</span>
                            </div>
                        </div>
                        <div class="blog-detail-hero">
                            <img src="${post.image_url || '/images/blog_fallback.png'}" alt="${post.title}" style="width:100%;">
                        </div>
                        <div class="blog-detail-content">
                            ${post.content}
                        </div>
                    `;
                } else {
                    blogPostContent.innerHTML = `<h1>Post Not Found</h1><p>The requested blog article was not found on our server. <a href="blog.html">Go back to blogs list</a>.</p>`;
                }
            })
            .catch(err => {
                console.error("Error reading single blog:", err);
                blogPostContent.innerHTML = `<h1>Error Loading Article</h1><p>There was a connection issue loading this article.</p>`;
            });
    }
});
