function save_cohort_fcns(cohort_name, time_points, subject)
    % Define a common figure size for all square images
    fig_size = 300; % Adjust this value as needed
    
    for time = time_points
        filename = sprintf('fcn_%s_subject_%d_time_%d.png', cohort_name, subject, time);
        figure('Position', [0, 0, fig_size, fig_size]);
        data = load(['normalize_' cohort_name '_subject_' num2str(subject) '_time_' num2str(time) '.txt']);
        
        % Create an axes that fills the entire square figure
        ax = axes('Position', [0, 0, 1, 1], 'Units', 'normalized');
        imagesc(ax, data);
        
        axis off;
        
        % Save the figure without white padding
        saveas(gcf, filename);
        close(gcf); % Close the figure to prevent display
    end    
    disp("Finished generating FCNs for: ");
    disp(cohort_name);
end
