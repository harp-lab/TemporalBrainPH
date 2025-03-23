function save_cohort_fcns(cohort_name, time_points, subject)
    for time = time_points
        filename = sprintf('fcn_%s_subject_%d_time_%d.png', cohort_name, subject, time);
        figure;
        data = load(['normalize_' cohort_name '_subject_' num2str(subject) '_time_' num2str(time) '.txt']);
        
        % Create an axes with tight fit to the data
        ax = axes('Position', [0, 0, 1, 1], 'Units', 'normalized');
        imagesc(ax, data);
        colorbar;
        axis off;
        
        % Save the figure without white padding
        set(gcf, 'Position', [0, 0, size(data, 2), size(data, 1)]);
        set(ax, 'Position', [0, 0, 1, 1]);        
        saveas(gcf, filename);
        close(gcf); % Close the figure to prevent display
    end    
    disp("Finished generating FCNs for: ");
    disp(cohort_name);
end


