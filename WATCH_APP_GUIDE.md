# Harrison's Medical RAG - Apple Watch App Guide

## 🎯 Goal

Build a native WatchOS app that:
1. Takes voice input (medical questions)
2. Searches Harrison's via your API
3. Displays results as a scrollable list
4. Shows page numbers when you select a result
5. Runs on YOUR watch only (no App Store needed)

---

## 📋 Prerequisites

### What You Need

- ✅ Mac with macOS (for Xcode)
- ✅ Xcode 15+ (free from Mac App Store - ~12GB download)
- ✅ Apple ID (free)
- ✅ iPhone paired with Apple Watch
- ✅ USB cable (to connect iPhone to Mac)

### Installation Steps

1. **Install Xcode:**
   ```
   Open Mac App Store → Search "Xcode" → Install (free)
   ```

2. **Setup Developer Account:**
   ```
   Open Xcode → Preferences → Accounts → Add Apple ID → Sign In
   ```
   
   You now have a FREE developer account! ✅

3. **Connect Your iPhone:**
   ```
   Plug iPhone into Mac via USB cable
   Trust computer on iPhone when prompted
   ```

---

## 🏗️ Phase 8: Create the WatchOS App

### Step 1: Create New Project

1. Open Xcode
2. **File → New → Project**
3. Select **watchOS → App**
4. Settings:
   - **Product Name:** HarrisonsWatch
   - **Organization Identifier:** com.yourname.harrisons
   - **Interface:** SwiftUI
   - **Language:** Swift
   - **Team:** Select your Apple ID account
5. Click **Create**

### Step 2: Project Structure

```
HarrisonsWatch/
├── HarrisonsWatch Watch App/
│   ├── HarrisonsWatchApp.swift       # Main app entry
│   ├── ContentView.swift             # Main view
│   ├── Models/
│   │   ├── APIClient.swift           # API communication
│   │   └── SearchModels.swift        # Data structures
│   ├── Views/
│   │   ├── SearchView.swift          # Search interface
│   │   ├── ResultsListView.swift     # Results display
│   │   └── TopicDetailView.swift     # Selected result details
│   └── Info.plist
```

---

## 💻 Code Implementation

### File 1: SearchModels.swift

Create `Models/SearchModels.swift`:

```swift
import Foundation

// Request to API
struct SearchRequest: Codable {
    let query: String
    let maxResults: Int
    
    enum CodingKeys: String, CodingKey {
        case query
        case maxResults = "max_results"
    }
}

// Single search result
struct TopicResult: Codable, Identifiable {
    let topicId: String
    let topicName: String
    let hierarchy: String
    let preview: String
    let pages: String
    let startPage: Int
    let endPage: Int
    let relevanceScore: Double
    let tables: [String]
    let figures: [String]
    
    var id: String { topicId }
    
    enum CodingKeys: String, CodingKey {
        case topicId = "topic_id"
        case topicName = "topic_name"
        case hierarchy, preview, pages
        case startPage = "start_page"
        case endPage = "end_page"
        case relevanceScore = "relevance_score"
        case tables, figures
    }
}

// API response
struct SearchResponse: Codable {
    let query: String
    let results: [TopicResult]
    let totalResults: Int
    let searchTimeMs: Int
    
    enum CodingKeys: String, CodingKey {
        case query, results
        case totalResults = "total_results"
        case searchTimeMs = "search_time_ms"
    }
}
```

---

### File 2: APIClient.swift

Create `Models/APIClient.swift`:

```swift
import Foundation

class APIClient: ObservableObject {
    // IMPORTANT: Replace with your Mac's IP address
    // Run this on your Mac to find it: ipconfig getifaddr en0
    private let baseURL = "http://192.168.1.XXX:8000"  // ← CHANGE THIS!
    
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    func search(query: String, maxResults: Int = 5) async throws -> SearchResponse {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        guard let url = URL(string: "\(baseURL)/api/search") else {
            throw URLError(.badURL)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 30 // 30 second timeout
        
        let searchRequest = SearchRequest(query: query, maxResults: maxResults)
        request.httpBody = try JSONEncoder().encode(searchRequest)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        
        guard httpResponse.statusCode == 200 else {
            errorMessage = "Server returned status \(httpResponse.statusCode)"
            throw URLError(.badServerResponse)
        }
        
        let searchResponse = try JSONDecoder().decode(SearchResponse.self, from: data)
        return searchResponse
    }
    
    func testConnection() async -> Bool {
        guard let url = URL(string: "\(baseURL)/health") else {
            return false
        }
        
        do {
            let (_, response) = try await URLSession.shared.data(from: url)
            if let httpResponse = response as? HTTPURLResponse {
                return httpResponse.statusCode == 200
            }
        } catch {
            print("Connection test failed: \(error)")
        }
        
        return false
    }
}
```

---

### File 3: SearchView.swift

Create `Views/SearchView.swift`:

```swift
import SwiftUI

struct SearchView: View {
    @StateObject private var apiClient = APIClient()
    @State private var searchQuery = ""
    @State private var searchResults: [TopicResult] = []
    @State private var isSearching = false
    @State private var showError = false
    
    var body: some View {
        NavigationView {
            VStack {
                // Search input with voice
                TextField("Ask about medicine", text: $searchQuery)
                    .textFieldStyle(.roundedBorder)
                    .padding(.horizontal)
                    .submitLabel(.search)
                    .onSubmit {
                        performSearch()
                    }
                
                // Loading indicator
                if isSearching {
                    ProgressView()
                        .padding()
                    Text("Searching Harrison's...")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                // Error message
                else if showError, let error = apiClient.errorMessage {
                    VStack {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.largeTitle)
                            .foregroundColor(.orange)
                        Text(error)
                            .font(.caption)
                            .multilineTextAlignment(.center)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                }
                // Results list
                else if !searchResults.isEmpty {
                    ResultsListView(results: searchResults)
                }
                // Empty state
                else {
                    VStack(spacing: 8) {
                        Image(systemName: "magnifyingglass")
                            .font(.title)
                            .foregroundColor(.secondary)
                        Text("Search Harrison's")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text("Try: \"hyponatremia workup\"")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                }
            }
            .navigationTitle("Harrison's")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
    
    private func performSearch() {
        guard !searchQuery.isEmpty else { return }
        
        isSearching = true
        showError = false
        
        Task {
            do {
                let response = try await apiClient.search(query: searchQuery, maxResults: 5)
                await MainActor.run {
                    searchResults = response.results
                    isSearching = false
                }
            } catch {
                await MainActor.run {
                    isSearching = false
                    showError = true
                    apiClient.errorMessage = "Check connection to Mac"
                }
            }
        }
    }
}
```

---

### File 4: ResultsListView.swift

Create `Views/ResultsListView.swift`:

```swift
import SwiftUI

struct ResultsListView: View {
    let results: [TopicResult]
    
    var body: some View {
        List(results) { result in
            NavigationLink(destination: TopicDetailView(topic: result)) {
                VStack(alignment: .leading, spacing: 4) {
                    // Topic name
                    Text(result.topicName)
                        .font(.caption)
                        .fontWeight(.semibold)
                        .lineLimit(2)
                    
                    // Page numbers
                    HStack {
                        Image(systemName: "book.fill")
                            .font(.caption2)
                        Text("Pages \(result.pages)")
                            .font(.caption2)
                        
                        Spacer()
                        
                        // Relevance indicator
                        RelevanceIndicator(score: result.relevanceScore)
                    }
                    .foregroundColor(.secondary)
                    
                    // Preview
                    Text(result.preview)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                }
                .padding(.vertical, 4)
            }
        }
    }
}

struct RelevanceIndicator: View {
    let score: Double
    
    var body: some View {
        HStack(spacing: 2) {
            ForEach(0..<3) { index in
                Image(systemName: index < Int(score * 3) ? "star.fill" : "star")
                    .font(.caption2)
                    .foregroundColor(.yellow)
            }
        }
    }
}
```

---

### File 5: TopicDetailView.swift

Create `Views/TopicDetailView.swift`:

```swift
import SwiftUI

struct TopicDetailView: View {
    let topic: TopicResult
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                // Header
                Text(topic.topicName)
                    .font(.headline)
                    .padding(.bottom, 4)
                
                // Hierarchy
                Label(topic.hierarchy, systemImage: "folder")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Divider()
                
                // Page information - THE MAIN OUTPUT
                VStack(alignment: .leading, spacing: 8) {
                    Label("Page Numbers", systemImage: "book.fill")
                        .font(.subheadline)
                        .fontWeight(.bold)
                    
                    HStack {
                        VStack(alignment: .leading) {
                            Text("Start:")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            Text("\(topic.startPage)")
                                .font(.title3)
                                .fontWeight(.bold)
                        }
                        
                        Spacer()
                        
                        Image(systemName: "arrow.right")
                            .foregroundColor(.secondary)
                        
                        Spacer()
                        
                        VStack(alignment: .trailing) {
                            Text("End:")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                            Text("\(topic.endPage)")
                                .font(.title3)
                                .fontWeight(.bold)
                        }
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(8)
                }
                
                Divider()
                
                // Preview
                VStack(alignment: .leading, spacing: 8) {
                    Label("Summary", systemImage: "doc.text")
                        .font(.subheadline)
                        .fontWeight(.bold)
                    
                    Text(topic.preview)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                // Tables if available
                if !topic.tables.isEmpty {
                    Divider()
                    VStack(alignment: .leading, spacing: 8) {
                        Label("Tables", systemImage: "tablecells")
                            .font(.subheadline)
                            .fontWeight(.bold)
                        
                        ForEach(topic.tables.prefix(3), id: \.self) { table in
                            Text("• \(table)")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                
                // Figures if available
                if !topic.figures.isEmpty {
                    Divider()
                    VStack(alignment: .leading, spacing: 8) {
                        Label("Figures", systemImage: "photo")
                            .font(.subheadline)
                            .fontWeight(.bold)
                        
                        ForEach(topic.figures.prefix(3), id: \.self) { figure in
                            Text("• \(figure)")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                
                Spacer()
                
                // Action instruction
                Text("📖 Open Harrison's PDF to pages \(topic.startPage)-\(topic.endPage)")
                    .font(.caption)
                    .foregroundColor(.blue)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(8)
            }
            .padding()
        }
        .navigationBarTitleDisplayMode(.inline)
    }
}
```

---

### File 6: Update ContentView.swift

Replace the content of `ContentView.swift`:

```swift
import SwiftUI

struct ContentView: View {
    var body: some View {
        SearchView()
    }
}

#Preview {
    ContentView()
}
```

---

### File 7: Update HarrisonsWatchApp.swift

Update `HarrisonsWatchApp.swift`:

```swift
import SwiftUI

@main
struct HarrisonsWatchApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

---

## ⚙️ Configuration

### Step 1: Find Your Mac's IP Address

```bash
# On your Mac terminal:
ipconfig getifaddr en0
# Example output: 192.168.1.105
```

### Step 2: Update APIClient.swift

In `APIClient.swift`, change this line:

```swift
private let baseURL = "http://192.168.1.105:8000"  // ← Your Mac's IP
```

### Step 3: Enable Networking

In Xcode:
1. Select your project in left sidebar
2. Select "HarrisonsWatch Watch App" target
3. Go to "Signing & Capabilities" tab
4. Click **"+ Capability"**
5. Add **"Outgoing Connections (Client)"**

---

## 🚀 Building & Installing

### Step 1: Select Your Device

In Xcode toolbar:
1. Click the device selector (top left)
2. Select your **iPhone** (not simulator)
3. Xcode will automatically install to paired Watch

### Step 2: Trust Developer Certificate

First time only:
1. On iPhone: **Settings → General → VPN & Device Management**
2. Find your Apple ID
3. Tap **"Trust [Your Name]"**

### Step 3: Build & Run

1. Click **Run ▶️** button (or press ⌘R)
2. Xcode compiles the app
3. Installs to iPhone
4. Syncs to Watch automatically
5. App appears on Watch home screen!

**⏱️ First build takes 2-3 minutes. Subsequent builds are faster.**

---

## 🧪 Testing

### 1. Start Your API Server

On Mac:
```bash
cd "/Users/maayan/medicinal rag/backend"
source venv/bin/activate
python main.py
```

### 2. Verify Connection

On Watch app:
- Type or dictate: **"hyponatremia"**
- Press search
- Should see results in ~2-3 seconds

### 3. Test Voice Input

- Tap the text field
- Start speaking
- Watch converts to text automatically
- Press search

---

## 📱 Usage Guide

### How to Use the Watch App

1. **Open app** on Watch (look for "HarrisonsWatch" icon)
2. **Tap search field** → speak or type your question
   - Example: "hyponatremia workup"
   - Example: "acute MI management"
3. **Results appear** as a scrollable list
4. **Scroll** with Digital Crown to see all results
5. **Tap a result** to see details
6. **Note the page numbers** (displayed prominently)
7. **Open Harrison's PDF** to those pages on your device

---

## 🔧 Troubleshooting

### App Won't Install

**Problem:** "Unable to install"  
**Solution:**
- Check iPhone is unlocked
- Check Watch is unlocked and on wrist
- Check USB cable connection
- Restart Xcode

### Can't Find Results

**Problem:** "Check connection to Mac"  
**Solution:**
1. Verify API is running on Mac
2. Check Mac's IP address hasn't changed
3. Ensure iPhone and Mac on same WiFi
4. Test: `curl http://YOUR_MAC_IP:8000/health` from iPhone Safari

### App Expired After 7 Days

**Problem:** "App needs to be reinstalled"  
**Solution:**
- Connect iPhone to Mac
- Click Run ▶️ in Xcode again
- OR: Pay $99/year for Apple Developer Program (apps last 1 year)

### Voice Input Not Working

**Problem:** Can't dictate  
**Solution:**
- On iPhone: **Settings → General → Keyboard → Enable Dictation**
- Try tapping the microphone icon in keyboard
- Speak clearly and wait for transcription

---

## 🎨 Customization Ideas

### Add Features

**Quick Queries:**
```swift
// Add preset buttons for common queries
Button("Hyponatremia") {
    searchQuery = "hyponatremia workup"
    performSearch()
}
```

**History:**
```swift
// Save recent searches
@AppStorage("searchHistory") var history: [String] = []
```

**Offline Mode:**
```swift
// Cache recent results
// Show "No connection" message gracefully
```

---

## ✅ Next Steps

### Phase 9: Optional Enhancements

1. **Add Voice-to-Text Integration** (Phase 10 of main roadmap)
2. **Deploy API to Cloud** (Phase 11) - for use outside home
3. **Add PDF Viewer** (Phase 12) - display actual PDF pages

### Phase 10: Production Deployment

If you want to use it anywhere (not just home WiFi):
- Deploy API to Google Cloud Run
- Update `baseURL` to cloud URL
- Access from anywhere!

---

## 💰 Cost Summary

| Item | Cost | When Needed |
|------|------|-------------|
| Mac + Xcode | Free | Already have |
| Free Developer Account | Free | Now |
| API Hosting (local) | Free | Now |
| **Paid Developer ($99/year)** | **$99** | **After 7 days if you love it** |
| Cloud deployment (optional) | ~$5-20/mo | Later if needed |

**Total to start: $0** ✅

---

## 🎉 Success!

You now have:
- ✅ Native Apple Watch app
- ✅ Voice search capability
- ✅ Real-time Harrison's lookup
- ✅ Page number retrieval
- ✅ Works on YOUR watch only (no App Store)

**Time to first working app: ~2-3 hours**

Questions? Check the troubleshooting section or review the code comments!

