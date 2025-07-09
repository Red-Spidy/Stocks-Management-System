use Stock_Management;
-- Market Table
CREATE TABLE Market (
    MarketId INT PRIMARY KEY,
    Type VARCHAR(50),
    Country VARCHAR(50)
);

-- Stocks Table
CREATE TABLE Stocks (
    StockId INT PRIMARY KEY,
    StockName VARCHAR(100),
    Price DECIMAL(10, 2),
    BrokerId INT,
    MarketId INT,
    FOREIGN KEY (MarketId) REFERENCES Market(MarketId)
);

-- Types Table
CREATE TABLE Types (
    TypeId INT PRIMARY KEY AUTO_INCREMENT,
    StockId INT,
    Indicator VARCHAR(50),
    Delivery VARCHAR(50),
    Quality VARCHAR(50),
    Lots INT,
    Quantity INT,
    Units VARCHAR(20),
    FOREIGN KEY (StockId) REFERENCES Stocks(StockId)
);

-- BrokerPlatform Table
CREATE TABLE BrokerPlatform (
    PlatformId INT PRIMARY KEY,
    Name VARCHAR(100),
    MobileNumber VARCHAR(15),
    Website VARCHAR(100),
    Commission DECIMAL(5, 2)
);

-- Information Table
CREATE TABLE Information (
    InfoId INT PRIMARY KEY AUTO_INCREMENT,
    BrokerId INT,
    StockId INT,
    BuyerId INT,
    FOREIGN KEY (BrokerId) REFERENCES BrokerPlatform(PlatformId),
    FOREIGN KEY (StockId) REFERENCES Stocks(StockId)
);

-- Buyer Table
CREATE TABLE Buyer (
    BuyerId INT PRIMARY KEY,
    Name VARCHAR(100),
    Email VARCHAR(100),
    MobileNumber VARCHAR(15),
    AadharId VARCHAR(20),
    Capital DECIMAL(15, 2),
    KYCStatus VARCHAR(20),
    PANNo VARCHAR(20),
    LinkedBankAccount VARCHAR(50),
    DematAccount VARCHAR(50),
    ProfitLoss DECIMAL(15, 2)
);

-- Portfolio Table
CREATE TABLE Portfolio (
    PortfolioId INT PRIMARY KEY AUTO_INCREMENT,
    BuyerId INT,
    StockId INT,
    Quantity INT,
    PurchasePrice DECIMAL(10, 2),
    FOREIGN KEY (BuyerId) REFERENCES Buyer(BuyerId),
    FOREIGN KEY (StockId) REFERENCES Stocks(StockId)
);

-- Dividend Table
CREATE TABLE Dividend (
    DividendId INT PRIMARY KEY AUTO_INCREMENT,
    BuyerId INT,
    Date DATE,
    Amount DECIMAL(10, 2),
    FOREIGN KEY (BuyerId) REFERENCES Buyer(BuyerId)
);

-- Buys Table
CREATE TABLE Buys (
    BuyerId INT,
    StockId INT,
    PRIMARY KEY (BuyerId, StockId),
    FOREIGN KEY (BuyerId) REFERENCES Buyer(BuyerId),
    FOREIGN KEY (StockId) REFERENCES Stocks(StockId)
);

-- Updates Table
CREATE TABLE Updates (
    StockId INT,
    PlatformId INT,
    PRIMARY KEY (StockId, PlatformId),
    FOREIGN KEY (StockId) REFERENCES Stocks(StockId),
    FOREIGN KEY (PlatformId) REFERENCES BrokerPlatform(PlatformId)
);

-- Has Table
CREATE TABLE Has (
    BuyerId INT,
    MobileNumber VARCHAR(15),
    PRIMARY KEY (BuyerId, MobileNumber),
    FOREIGN KEY (BuyerId) REFERENCES Buyer(BuyerId)
);
