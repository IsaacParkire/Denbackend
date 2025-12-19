document.addEventListener('DOMContentLoaded', function() {
    const mainCategoryField = document.querySelector('#id_main_category');
    const subCategoryField = document.querySelector('#id_sub_category');

    if (mainCategoryField && subCategoryField) {
        function updateSubCategories() {
            const mainCategoryId = mainCategoryField.value;
            const subCategorySelect = subCategoryField;

            // Clear current options except the first (empty)
            subCategorySelect.innerHTML = '<option value="">---------</option>';

            if (mainCategoryId) {
                // Fetch subcategories for the selected main category
                fetch(`/api/products/sub-categories/?main_category=${mainCategoryId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.results) {
                            // Paginated response
                            data.results.forEach(subCategory => {
                                const option = document.createElement('option');
                                option.value = subCategory.id;
                                option.textContent = subCategory.name;
                                subCategorySelect.appendChild(option);
                            });
                        } else {
                            // Direct array response
                            data.forEach(subCategory => {
                                const option = document.createElement('option');
                                option.value = subCategory.id;
                                option.textContent = subCategory.name;
                                subCategorySelect.appendChild(option);
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching subcategories:', error);
                        // Fallback: show all subcategories
                        fetch('/api/products/sub-categories/')
                            .then(response => response.json())
                            .then(data => {
                                if (data.results) {
                                    data.results.forEach(subCategory => {
                                        const option = document.createElement('option');
                                        option.value = subCategory.id;
                                        option.textContent = subCategory.name;
                                        subCategorySelect.appendChild(option);
                                    });
                                } else {
                                    data.forEach(subCategory => {
                                        const option = document.createElement('option');
                                        option.value = subCategory.id;
                                        option.textContent = subCategory.name;
                                        subCategorySelect.appendChild(option);
                                    });
                                }
                            })
                            .catch(error => console.error('Error fetching all subcategories:', error));
                    });
            } else {
                // If no main category selected, show all subcategories
                fetch('/api/products/sub-categories/')
                    .then(response => response.json())
                    .then(data => {
                        if (data.results) {
                            data.results.forEach(subCategory => {
                                const option = document.createElement('option');
                                option.value = subCategory.id;
                                option.textContent = subCategory.name;
                                subCategorySelect.appendChild(option);
                            });
                        } else {
                            data.forEach(subCategory => {
                                const option = document.createElement('option');
                                option.value = subCategory.id;
                                option.textContent = subCategory.name;
                                subCategorySelect.appendChild(option);
                            });
                        }
                    })
                    .catch(error => console.error('Error fetching subcategories:', error));
            }
        }

        mainCategoryField.addEventListener('change', updateSubCategories);

        // Update on page load if main category is already selected
        if (mainCategoryField.value) {
            updateSubCategories();
        } else {
            // Show all subcategories initially
            updateSubCategories();
        }
    }
});