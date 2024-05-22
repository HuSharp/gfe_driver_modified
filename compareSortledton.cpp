#include<bits/stdc++.h>
using namespace std;

int main(){
    map<long long,int> myresult, sortledton;
    fstream file;
    file.open("bfs_results_graphstore.txt",ios::in);
    string line;
    while(getline(file, line)){
        stringstream lin(line);
        long long dst; int dist;
        lin>>dst>>dist;
        myresult[dst]=dist; 
    }
    fstream file_2;

    file_2.open("bfs_results_sortledton.txt",ios::in);
    while(getline(file_2, line)){
        stringstream lin(line);
        // cout<<line<<endl;
        long long dst; int dist;
        lin>>dst>>dist;
        // break;
        sortledton[dst]=dist; 
    }
    // cout<<sortledton[3442799]<<endl;
    for(auto x: myresult)
        if(sortledton[x.first]!=x.second)
        {
            cout<<x.first<<" "<<x.second<<" "<<sortledton[x.first]<<endl;
            break;
        }

}