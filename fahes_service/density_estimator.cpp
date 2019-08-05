/**************************************
 **** 2017-6-6      ******************
 **** Abdulhakim Qahtan ****************
 **** aqahtan@hbku.edu.qa ****************
 ***************************************/

#include "density_estimator.h"



// ==============================================================
double Den_Estimator::compute_bandwidth(double std, long n){
	if (std == 0)	return 1.0;
	double bandwidth = (double)(2.345 * std * pow(n, -0.2));
	return bandwidth;
}


// ==============================================================
double Den_Estimator::compute_max_pdf(map <double, long> & col_profile, 
				double min_val, double max_val, double h){
	long n = 100;
	double eval_step = (max_val - min_val) / (double)(n);
	double max_pdf = 0, pdf;
	long S = col_profile.size();
	for (double e_pnt = min_val; e_pnt < max_val; e_pnt += eval_step){
		pdf = evaluate_pnt(col_profile, e_pnt, h, S);
		if (max_pdf < pdf)
			max_pdf = pdf;
	}
	return max_pdf;
}




// ==============================================================

double Den_Estimator::evaluate_pnt(map <double, long> & col_profiler, const double & x,
					const double & h, const long & S){
	double epdf; 
	map <double, long>::iterator itr;
	double sum = 0.0;
	for (itr = col_profiler.begin(); itr != col_profiler.end(); itr++){
		sum += kernel_func((x - itr->first) / h) / h * itr->second;
	}
	epdf = (sum / ((double)S));
	// cout << x << '\t' << epdf << endl;
	return epdf;
}



// ==============================================================
vector<sus_disguised> Den_Estimator::density_based_od(const string Attribute, map<double, long> & col_profile,
										map<string, long> & common, 
    									const double & std){
	vector<sus_disguised> sus_disg;
	int num_distinct_vals = col_profile.size();
	map<string, long>::iterator str_itr;
	map<double, long>::iterator dbl_itr1, temp_dbl_itr, tt_dbl_itr;
	den_func::iterator dbl_itr2;

	// den_func df;
	const int ensembles = 4;
	den_val dv;
	sus_disguised sus_val;
	long S = 0, outlier_freq;
	double epdf, val, max_score = 0, f_i, min_val, max_val, f_max;
	string outlier;
	double min_dist = std, score;
	temp_dbl_itr = col_profile.begin();
	tt_dbl_itr = col_profile.end();
	tt_dbl_itr--;
	min_val = temp_dbl_itr->first;
	max_val = tt_dbl_itr->first;
	for (dbl_itr1 = col_profile.begin(); dbl_itr1 != col_profile.end(); dbl_itr1++){
		S += dbl_itr1->second;
		temp_dbl_itr ++;
		if (temp_dbl_itr != col_profile.end())
			min_dist = MIN(min_dist, std::abs(temp_dbl_itr->first - dbl_itr1->first));
	}	
	double h0 = compute_bandwidth(std, S);
	f_max = compute_max_pdf(col_profile, min_val, max_val, h0);
	if ((min_dist <= h0) && (col_profile.size() > 10)){
		for (str_itr = common.begin(); str_itr != common.end(); str_itr++){
			epdf = f_max;
			if (!isNumber(str_itr->first))		continue;
			for (int kk = 0; kk < ensembles; kk++){
				val = convert_to_double(str_itr->first);
				double h = h0 - (0.2 * kk *h0);
				f_i = evaluate_pnt(col_profile, val, h, S);
				if (epdf > f_i)
					epdf = f_i;
			}
			score = MAX(f_max - epdf, 0.0) / f_max;
			if (score > max_score){
				max_score = score;
				outlier = str_itr->first;
				outlier_freq = str_itr->second;
			}

			      
		}
		if (max_score > (1.0 - 1E-16)){
			sus_disguised sus_dis_struct;
		    sus_dis_struct.attr_name = Attribute;
		    sus_dis_struct.value = outlier;
		    sus_dis_struct.score = max_score;
		    sus_dis_struct.frequency = outlier_freq;
		    sus_dis_struct.tool_name = "OD";
		    sus_disg.push_back(sus_dis_struct);
		}   
		
	}
	return sus_disg;
}

