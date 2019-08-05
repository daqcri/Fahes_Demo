/**************************************
 **** 2017-6-5      ******************
 **** Abdulhakim Qahtan ****************
 **** aqahtan@hbku.edu.qa ****************
 ***************************************/

#include "OD.h"
#include "density_estimator.h"

// ========================================================================

void OD::compute_statistical_quantities(map<double, long> & col_profile, double & mean, 
    									double & std){
	double sum = 0, sq_sum = 0;
	
	map<double, long>::iterator dbl_itr;
	long num_tuples = 0;
	dbl_itr = col_profile.begin();
	while (dbl_itr != col_profile.end()){
		sum += dbl_itr->first * dbl_itr->second;
		num_tuples += dbl_itr->second;
		sq_sum += pow(dbl_itr->first, EX) * dbl_itr->second;
		dbl_itr ++;
	}
	mean = sum / (double) num_tuples;
	std = compute_std(sum, sq_sum, num_tuples);
	// cerr << "Mean = " << mean << "\t STD = " << "\t Num. tuples = " << num_tuples << endl; 
}


// ========================================================================
void OD::detect_outliers(TableProfile & TP, 
    			std::vector<sus_disguised> & sus_dis_values){
	
	map<double, long> numeric_data;
	map<double, long>::iterator dbl_itr;	//, dbl_ir2;
	vector<sus_disguised> sus_disg;
	vector<vector<sus_disguised> >	od_dvd(num_od_tools);
	double mean, std;
	long L_Str, L_Nums;
	for (long i = 0; i < (long)TP.header.size(); i++){
		L_Str = TP.profile[i].distinct_Strings.size();
		L_Nums = TP.profile[i].distinct_Numbers.size();
		
		if (L_Str < num_non_ignorable_strings){
			dbl_itr = TP.profile[i].distinct_Numbers.begin();
			while (dbl_itr != TP.profile[i].distinct_Numbers.end()){
				numeric_data[double(dbl_itr->first)] = dbl_itr->second;
				dbl_itr ++;
			}		
			if ((long)numeric_data.size() >= least_num_values){
				compute_statistical_quantities(numeric_data, mean, std);
				
				Den_Estimator DE;
				sus_disg = DE.density_based_od(TP.header[i], numeric_data, TP.profile[i].common_Strings, std);
				// ================ For testing the density estimator =======================
				for (int k = 0; k < (long)sus_disg.size(); k++){
					add_sus_struct(sus_disg[k].attr_name, sus_disg[k].value, sus_disg[k].score, 
						sus_disg[k].frequency, sus_disg[k].tool_name, sus_dis_values);
				}
				// cerr << TP.header[i] << "::Min = " << min_val << "::Max = " << max_val << endl;
			}
			numeric_data.clear();
			sus_disg.clear();
		}
	}
}



