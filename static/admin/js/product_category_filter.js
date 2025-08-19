// Dynamic filtering for subcategories based on main category selection
(function($) {
    'use strict';
    
    function filterSubCategories() {
        var mainCategoryField = $('#id_main_category');
        var subCategoryField = $('#id_sub_category');
        
        if (!mainCategoryField.length || !subCategoryField.length) {
            return;
        }
        
        function updateSubCategories() {
            var mainCategoryId = mainCategoryField.val();
            var currentSubCategoryId = subCategoryField.val();
            
            // Clear existing options except the empty one
            subCategoryField.find('option:not([value=""])').remove();
            
            if (mainCategoryId) {
                // Fetch subcategories via AJAX
                $.get('/admin/api/subcategories/', {
                    main_category: mainCategoryId
                }, function(data) {
                    $.each(data, function(index, subcategory) {
                        var selected = currentSubCategoryId == subcategory.id ? 'selected' : '';
                        subCategoryField.append(
                            '<option value="' + subcategory.id + '" ' + selected + '>' + 
                            subcategory.name + '</option>'
                        );
                    });
                }).fail(function() {
                    // Fallback: show all subcategories
                    console.log('Failed to load subcategories');
                });
            }
        }
        
        // Initial load
        updateSubCategories();
        
        // Update on main category change
        mainCategoryField.on('change', updateSubCategories);
    }
    
    // Initialize when the DOM is ready
    $(document).ready(function() {
        filterSubCategories();
    });
    
})(django.jQuery);
