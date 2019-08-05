/**************************************
 **** 2017-4-23      ******************
 **** Abdulhakim Qahtan ****************
 **** aqahtan@hbku.edu.qa ****************
 ***************************************/


#include "csv_reader.h"
#include "Profiler.h"
#include "common.h"
#include "DV_Detector.h"
#include "OD.h"
#include "RandomDMV.h"
#include "Patterns.h"
 long max_num_terms_per_att = 200;



// ========================================================================
string splitpath(const std::string str, 
                  const char delimiter){
    int i, j, k;
    // cout << str << endl;
    for(i = str.length(); i >= 0; i --){
        if (delimiter == str[i])
            break;
    }
    // cout << "i = " << i << "   string length = " << str.length() << endl;
    if ((i == 0) && (str[i] != delimiter)) i = -1;  
    std::string result = str.substr (i+1,str.length()-1);
    return result;
}

// ========================================================================
// void Print_output_data(string output_dir, string tab_name, std::vector<sus_disguised> sus_dis_values){
//     if (output_dir[output_dir.length()-1] != '/')
//         output_dir += '/';
//     char delim = '/';
//     string out_f_name = splitpath(tab_name, delim);
//     out_f_name = "DMV_"+out_f_name;
//     string out_file_name = output_dir + out_f_name;
//     fstream ofs(out_file_name, ios::out);
//     if (!ofs.good()){
//         cerr << "Problem opening output file .... \n" << out_file_name << endl;;
//         return;
//     }
//     ofs << "attribute name, DMV, frequency" << endl;
//     // ofs << "FAHES_V1" << endl;
//     if (sus_dis_values.size() < 1) {
//         ofs << ",," << endl;
//     } else {
//         ofs << sus_dis_values[0].attr_name << "," 
//             << check_d_quotation(sus_dis_values[0].value) << "," 
//             << sus_dis_values[0].frequency
//             // << "," << sus_dis_values[0].score
//             // << "," << sus_dis_values[0].tool_name 
//             << endl;
//         for (long i = 1; i < (long)sus_dis_values.size(); i++)
//             ofs << sus_dis_values[i].attr_name << "," 
//                 << check_d_quotation(sus_dis_values[i].value) << "," 
//                 << sus_dis_values[i].frequency
//                 // << "," << sus_dis_values[i].score
//                 // << "," << sus_dis_values[i].tool_name 
//                 << endl;
//     }    
//     ofs.close();
// }



// ========================================================================
void Print_output_data(string output_dir, string tab_name, vector<sus_disguised> sus_dis_values, 
                    vector < map<string, long> > ptrns, vector<string> T_Header){
    if (output_dir[output_dir.length()-1] != '/')
        output_dir += '/';
    char delim = '/';
    string out_f_name = splitpath(tab_name, delim);
    string table_name = out_f_name.substr (0,out_f_name.length()-4);
    // cerr << table_name << endl;
    out_f_name = "DMV_"+table_name+".json";
    string out_file_name = output_dir + out_f_name;
    fstream ofs(out_file_name, ios::out);
    if (!ofs.good()){
        cerr << "Problem opening output file .... \n" << out_file_name << endl;;
        return;
    }
    if (sus_dis_values.size() < 1)
        return;
    ofs << "{\n\"DMVs\":\n [\n";
    for (size_t i = 0; i < sus_dis_values.size()-1; i++){
        ofs << "{\n" << "\"DMV\":\n[\"" << sus_dis_values[i].attr_name
            << "\", \"" << sus_dis_values[i].value
            << "\",\"" << sus_dis_values[i].frequency
             // << "," << sus_dis_values[i].score
            << "\",\"" << sus_dis_values[i].tool_name 
            << "\"]\n},\n";
    }
    size_t k = sus_dis_values.size()-1;
    ofs << "{" << "\"DMV\":\n[\"" << sus_dis_values[k].attr_name
            << "\",\"" << sus_dis_values[k].value
            << "\",\"" << sus_dis_values[k].frequency
             // << "," << sus_dis_values[i].score
            << "\",\"" << sus_dis_values[k].tool_name 
            << "\"]\n}\n";
    ofs << "],";
    ofs << "\n\"PTRNs\":\n [\n";
    if (ptrns.size() > 0){
        for (size_t i = 0; i < T_Header.size()-1; i++){
            ofs << "{\n" << "\"PTRN\":\n[\"" << T_Header[i] << "\"";
            map<string, long>::iterator itr = ptrns[i].begin();
            while(itr != ptrns[i].end()){
                ofs << ", \"" << itr->first
                    << "\",\"" << itr->second<< "\"";
                    // << "," << sus_dis_values[i].score
                    itr ++;
                }
                ofs << "]\n},\n";
        }
        k = T_Header.size()-1;
        ofs << "{\n" << "\"PTRN\":\n[\"" << T_Header[k] << "\"";
            map<string, long>::iterator itr = ptrns[k].begin();
            while(itr != ptrns[k].end()){
                ofs << ", \"" << itr->first
                    << "\",\"" << itr->second << "\"";
                    // << "," << sus_dis_values[i].score
                    itr ++;
                }
        ofs << "]\n}\n";
    }
    ofs << "]\n}\n";
    // ofs.close();
}



// ================The main Function====================================
extern "C"
void execute(char * table_name, char * out_directory) {
    
    string file_name = string(table_name);
    string output_dir = string(out_directory);
    fstream log_fid;
    log_fid.open("running_fahes.log", ios::out);
    if (!log_fid.good()){
        cerr << "Problem opening log file .... \n";
        return;
    }

    // if (debug)
        log_fid << file_name << "::" << output_dir << endl;
    // string s = "ERIN";
    // transform( s.begin(), s.end(), s.begin(), ::tolower );
    // cerr << "Checking " << s << "\t" << check_str_repetition(s) << endl;
    // return ;
    string full_output_path = realpath(output_dir.c_str(), NULL);

    std::vector<sus_disguised> sus_dis_values;
    while(!sus_dis_values.empty())
        sus_dis_values.pop_back();

    // fstream ofs(output_file_name, ios::out);
    // if (!ofs.good())
    // {
    //   cerr << "Unable to open output file .. \n";
    //   return 0;
    // }
    doubleVecStr P;
    // cout << "Check 1" << endl;
    CSV_READER *dataReader = new CSV_READER();  
    Table T = dataReader->read_csv_file(file_name);
    log_fid << T.table_name << "  has : " << T.data[0].size() << "  attributes" 
         << "  and  " << T.data.size() << "  Tuples." << endl;

    RandomDMV RandDMV;
    DataProfiler * dvdDataProfiler = new DataProfiler();
    TableProfile TP;
    vector<struct item> most_common;
    DV_Detector DVD;
    OD od;
    vector<map<string, long> > tablehist =  dvdDataProfiler->TableHistogram(T);
    TP = dvdDataProfiler->profile_table(T, tablehist);
    pattern_learner * PL = new pattern_learner();
    
    sus_dis_values = RandDMV.find_disguised_values(T, tablehist, max_num_terms_per_att);
    vector < map<string, long> > all_ptrns;
    all_ptrns = PL->find_all_patterns(tablehist, TP, sus_dis_values);
    DVD.check_non_conforming_patterns(TP, tablehist, sus_dis_values);
    od.detect_outliers(TP, sus_dis_values);
    

    // Print_output_data(sus_dis_values, all_ptrns, T.header);
    Print_output_data(full_output_path, T.table_name, sus_dis_values, all_ptrns, T.header);
             // << sus_dis_values[i].score << endl;
    // for (int i = 0; i < TP.number_of_atts; i ++){
    //     cout << TP.header[i] << endl;
    //     // if (TP.header[i] == "Plasma glucose concentration"){
    //     map<string, long>::iterator string_itr = TP.profile[i].common_Strings.begin();
    //     while (string_itr != TP.profile[i].common_Strings.end()){
    //         cout << string_itr->first << '\t' << string_itr->second << endl;
    //         string_itr ++;
    //     }
    //     cout << "=================================\n";   
    // }
    // cerr << "Freqs = " << TP.profile[7].freq_of_freq.size() << endl;
    // map<double, long>::iterator dbl_itr = TP.profile[7].freq_of_freq.begin();
    // for (;dbl_itr != TP.profile[7].freq_of_freq.end(); dbl_itr++)
    //     cout << dbl_itr->first << '\t' << dbl_itr->second << endl;
    // cout << "=================================\n"; 

    // map<string, long>::iterator s_itr = tablehist[7].begin();
    // for (;s_itr != tablehist[7].end(); s_itr++)
    //     cout << s_itr->first << '\t' << s_itr->first.length() << '\t' << s_itr->second << endl;
    // cout << "=================================\n";
    log_fid.close();
}
