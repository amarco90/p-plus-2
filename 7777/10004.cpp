#include <iostream>
#include <vector>

using namespace std;

int n, e, x, y;
vector<int> neighbours[200];
bool possible;
int color[200]; // -1 if not painted

void paint(int node, int c) { // we paint with color 0 or 1
	color[node] = c;
	vector<int> neig = neighbours[node];
	for(int i=0; i<neig.size(); ++i) {
		if(color[neig[i]] == -1) {
			paint(neig[i], !c);
		}
		else if(color[neig[i]] == c) {
			possible = false;
			return;
		}
	}
}

int main() {
	while(cin>>n && n) {
		for(int i=0; i<n; ++i) {
			neighbours[i].clear();
			color[i] = -1;
		}
		possible = true;
		
		cin>>e;
		for(int i=0; i<e; ++i) {
			cin >> x >> y;
			neighbours[x].push_back(y);
			neighbours[y].push_back(x);
		}
		paint(0, 0); // paint node 0 with color 0
		cout << ((possible)? "BICOLORABLE" : "NOT BICOLORABLE") << ".\n";
	}
}