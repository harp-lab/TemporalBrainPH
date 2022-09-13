conn_dfc = load("../dynamic_FC_1400.mat").conn_dfc_data_1400;
conn_dfc(:, 24, :, :) = [];
conn_dfc(:, :, 24, :) = [];
count = 0;

[number_of_time_points, number_of_rois_1, number_of_rois_2, number_of_subjects] = size(conn_dfc);
for i = 1:number_of_subjects
    M = zeros(number_of_time_points, number_of_rois_1, number_of_rois_2);
    for j = 1:number_of_rois_1
        for k = 1:number_of_rois_2
            for l = 1:number_of_time_points
                current_val = conn_dfc(l, j, k, i);
                M(l, j, k) = current_val;
            end
        end
    end
    for j = 1:number_of_time_points
        filename = "../dfc_1400_normal/normalize_dfc_1400_subject_" + i + "_time_"+j+".txt";
        time_data = reshape(M(j,:,:), [number_of_rois_1, number_of_rois_2]);
        subject_data = corrcoef(transpose(time_data));
        subject_data_normalize = sqrt(1 - subject_data.*subject_data);
        writematrix(subject_data_normalize, filename, 'Delimiter', 'tab');
        count = count + 1;
    end
    disp("Done writing normalized files for subject "+i);
end
disp("Number of time points: " + number_of_time_points);
disp("ROI 1: "+number_of_rois_1);
disp("ROI 2: "+number_of_rois_2);
disp("Number of subjects: " + number_of_subjects);
disp("Total wrote "+count+" files");

