function save_cohort_fcns(cohort_name, time_points, subject)
    for time = time_points
        filename = sprintf('fcn_%s_subject_%d_time_%d.png', cohort_name, subject, time);
        figure;
        data = load(['normalize_' cohort_name '_subject_' num2str(subject) '_time_' num2str(time) '.txt']);
        imagesc(data);
        colorbar;
        axis off;
        saveas(gcf, filename);
        close(gcf); % Close the figure to prevent display
    end    
    disp("Finished generating FCNs for: ");
    disp(cohort_name);
end


