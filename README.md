# Cashflow Commander 💰

A sophisticated financial management web application designed specifically for micro-business owners who need simple yet powerful cash flow tracking and visualization.

## Features ✨

### 🎯 Core Functionality
- **Transaction Management**: Add, edit, and delete income/expense transactions
- **Real-time Dashboard**: Live financial metrics and visualizations
- **Cash Flow Analysis**: Waterfall charts and trend analysis
- **Monthly Reports**: Comprehensive financial summaries with export capabilities
- **Data Persistence**: SQLite database for reliable local storage

### 📊 Visualizations
- **Line Charts**: Cumulative balance trends over time
- **Waterfall Charts**: Income vs Expenses by category
- **Key Metrics**: Net cash flow, total income, total expenses, current balance
- **Interactive Filters**: Date and category-based filtering

### 🔧 Technical Features
- **CRUD Operations**: Full Create, Read, Update, Delete functionality
- **Session Management**: Real-time data updates across all components
- **Data Validation**: Input validation and error handling
- **Export Capabilities**: CSV export for accountant integration
- **Responsive Design**: Mobile-friendly interface

## Technology Stack 🛠️

- **Frontend**: Streamlit (latest version)
- **Database**: SQLite3 (self-contained, local database)
- **Data Processing**: Pandas for data manipulation
- **Visualizations**: Plotly Express for interactive charts
- **Styling**: Custom CSS with professional design

## Installation & Setup 🚀

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone or download the application files**
   ```bash
   # Create a new directory
   mkdir cashflow-commander
   cd cashflow-commander
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:8501`
   - The application will automatically create the database on first run

## Usage Guide 📖

### Getting Started
1. **First Run**: The application will initialize with sample categories
2. **Add Transactions**: Use the "Add Transaction" section to input income and expenses
3. **View Dashboard**: Monitor your financial health in real-time
4. **Manage Ledger**: Edit or delete transactions as needed
5. **Generate Reports**: Export monthly summaries for your accountant

### Navigation
- **📈 Dashboard**: Overview with charts and key metrics
- **💳 Add Transaction**: Form to add new income/expense entries
- **📋 Ledger**: Complete transaction history with editing capabilities
- **📊 Reports**: Monthly summaries and data export

### Transaction Categories

**Income Categories:**
- Sales
- Services
- Other Income

**Expense Categories:**
- Rent
- Supplies
- Utilities
- Marketing
- Insurance
- Other Expense

## Database Schema 🗄️

### Transactions Table
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('Income', 'Expense')),
    category TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Categories Table
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('Income', 'Expense'))
)
```

## Key Features Explained 🔍

### Dashboard Analytics
- **Net Cash Flow**: Real-time calculation of income minus expenses
- **Cumulative Balance**: Running total of all transactions over time
- **Category Analysis**: Visual breakdown of spending and income by category
- **Trend Visualization**: Line charts showing financial trajectory

### Data Management
- **Editable Ledger**: Inline editing of transaction details
- **Bulk Operations**: Filter and sort transactions
- **Data Validation**: Ensures data integrity and prevents errors
- **Backup & Export**: CSV export for external analysis

### User Experience
- **Intuitive Interface**: Clean, professional design
- **Real-time Updates**: Instant dashboard updates after changes
- **Mobile Responsive**: Works on desktop, tablet, and mobile
- **Error Handling**: Comprehensive error messages and validation

## Customization 🎨

### Adding New Categories
Categories are stored in the database and can be extended by:
1. Modifying the `init_database()` method in `database.py`
2. Adding new category entries to the default categories list

### Styling Customization
The application uses custom CSS that can be modified in the `app.py` file:
- Colors and themes
- Typography
- Layout and spacing
- Component styling

### Chart Customization
Plotly charts can be customized by modifying the chart creation code:
- Color schemes
- Chart types
- Interactive features
- Layout options

## Troubleshooting 🔧

### Common Issues
1. **Database Connection**: Ensure write permissions in the application directory
2. **Port Conflicts**: Streamlit default port (8501) might be in use
3. **Dependencies**: Verify all required packages are installed

### Solutions
- **Port Change**: Use `streamlit run app.py --server.port 8502`
- **Database Issues**: Delete `cashflow.db` to reset (data will be lost)
- **Package Issues**: Reinstall requirements with `pip install -r requirements.txt`

## Security & Privacy 🔒

- **Local Storage**: All data stored locally on your machine
- **No External Calls**: No data transmitted to external services
- **File Permissions**: Database file permissions handled by operating system
- **Data Ownership**: You maintain complete control of your financial data

## Future Enhancements 🚀

Potential features for future versions:
- Budget planning and forecasting
- Receipt scanning and OCR
- Multi-user support
- Cloud synchronization
- Advanced analytics and insights
- Integration with accounting software
- Mobile app companion

## Support & Contribution 🤝

This application is designed to be self-contained and easy to use. For technical issues:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure proper file permissions
4. Restart the application if needed

## License 📄

This project is open source and available for modification and distribution. Feel free to adapt it for your specific business needs.

---

**Cashflow Commander** - Empowering micro-business financial management through intuitive technology. 💪📊