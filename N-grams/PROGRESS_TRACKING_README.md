# 📊 Progress Tracking System

This document explains how to use the new progress tracking system that has been added to your N-grams typing application.

## 🎯 What It Tracks

The system automatically records the following data for every typing test:

- **WPM (Words Per Minute)**: Your typing speed
- **Accuracy**: Percentage of correctly typed characters
- **Characters Typed**: Total number of characters typed
- **Time Taken**: Actual time spent typing
- **Date Taken**: When the test was completed
- **Difficulty Level**: Easy, Medium, or Hard
- **N-Gram Order**: The N-gram model used (2-5)
- **Test Duration**: Time limit for the test

## 🚀 How to Use

### 1. Automatic Data Collection

**No setup required!** The system automatically saves your progress after every typing test. Simply:
1. Run typing tests from the main menu
2. Complete the tests
3. Your results are automatically saved

### 2. View Your Progress

#### Option A: Quick Progress Summary
- From main menu, select **"Quick Progress Summary"**
- See your key stats at a glance
- Press Enter to return to main menu

#### Option B: Full Progress Dashboard
- From main menu, select **"View Progress Dashboard"**
- Access comprehensive statistics and analysis
- Navigate through different views

### 3. Dashboard Features

The progress dashboard provides:

- **Overall Statistics**: Total tests, best scores, averages
- **Recent Performance**: Last 10 tests performance
- **Difficulty Breakdown**: Performance by difficulty level
- **Test History**: Detailed list of recent tests
- **Data Export**: Export to CSV or JSON format

## 📁 Data Storage

### File Locations
- **Main Data**: `typing_progress.json`
- **Backup**: `typing_progress_backup.json`

### Data Protection
- **Automatic Backups**: Created before every save
- **Corruption Recovery**: Automatically restores from backup if main file is corrupted
- **Atomic Saves**: Uses temporary files to prevent data loss during saves
- **File Size Management**: Keeps last 1000 tests to prevent excessive file growth

## 🔧 Technical Details

### Data Structure
```json
{
  "version": "1.0",
  "created_date": "2024-01-01T00:00:00",
  "total_tests": 0,
  "best_wpm": 0.0,
  "best_accuracy": 0.0,
  "average_wpm": 0.0,
  "average_accuracy": 0.0,
  "total_characters": 0,
  "total_time": 0.0,
  "test_history": []
}
```

### Backup Strategy
1. **Before Save**: Creates backup of current data
2. **Save Process**: Writes to temporary file, then atomically replaces main file
3. **Error Recovery**: If save fails, restores from backup
4. **Corruption Detection**: Automatically detects and recovers from corrupted files

## 📊 Understanding Your Stats

### WPM (Words Per Minute)
- **Beginner**: 20-40 WPM
- **Intermediate**: 40-60 WPM
- **Advanced**: 60-80 WPM
- **Expert**: 80+ WPM

### Accuracy
- **Excellent**: 95%+
- **Good**: 90-94%
- **Fair**: 80-89%
- **Needs Improvement**: Below 80%

### Progress Tracking Tips
- Take tests regularly to see improvement trends
- Compare performance across different difficulty levels
- Focus on accuracy first, then speed
- Use the difficulty analysis to identify areas for improvement

## 🚨 Troubleshooting

### Common Issues

#### "Progress tracking not working"
- Check if `progress_tracker.py` exists in your project folder
- Ensure you have write permissions in the project directory
- Run `test_progress.py` to diagnose issues

#### "No data available"
- Take at least one typing test first
- Check if the JSON files were created
- Verify file permissions

#### "Import errors"
- Make sure all required Python modules are available
- Check that `progress_tracker.py` and `progress_dashboard.py` are in the same directory

### Testing the System
Run the test script to verify everything works:
```bash
python test_progress.py
```

## 📈 Data Export

### CSV Export
- Compatible with Excel, Google Sheets, and other spreadsheet applications
- Contains all test data in tabular format
- Useful for detailed analysis and graphing

### JSON Export
- Raw data format for custom analysis
- Can be imported into other applications
- Preserves all metadata and structure

## 🔮 Future Enhancements

Potential improvements that could be added:
- **Charts and Graphs**: Visual representation of progress
- **Goal Setting**: Set WPM and accuracy targets
- **Practice Recommendations**: AI-suggested practice areas
- **Social Features**: Compare with friends or global averages
- **Mobile App**: Sync progress across devices

## 📝 Example Usage

### Running a Test
1. Start the main program: `python main.py`
2. Select "Start typing test (30/60/120s)"
3. Choose time limit and difficulty
4. Complete the typing test
5. Results are automatically saved

### Viewing Progress
1. From main menu, select "View Progress Dashboard"
2. Browse through different sections
3. Export data if needed
4. Return to main menu when done

### Quick Check
1. From main menu, select "Quick Progress Summary"
2. See key stats immediately
3. Press Enter to continue

## 🎉 Benefits

- **Motivation**: See your improvement over time
- **Analysis**: Identify strengths and weaknesses
- **Goal Setting**: Track progress toward typing goals
- **Data Backup**: Never lose your progress data
- **Portability**: Export data for external analysis

---

**Note**: The progress tracking system is designed to be robust and user-friendly. It automatically handles most edge cases and provides fallback mechanisms to ensure your data is always safe.

