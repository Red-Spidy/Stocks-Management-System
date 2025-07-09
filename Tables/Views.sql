CREATE VIEW ViewBuyerPortfolio AS
SELECT 
    b.BuyerId,
    b.Name AS BuyerName,
    p.StockId,
    p.StockName,
    SUM(p.Quantity) AS TotalQuantity,
    SUM(p.Quantity * p.PurchasePrice) AS TotalInvestment
FROM Buyer b
JOIN Portfolio p ON b.BuyerId = p.BuyerId
GROUP BY b.BuyerId, p.StockId;

CREATE VIEW ViewStockMarket AS
SELECT 
    s.StockId,
    s.StockName,
    s.Price,
    m.Type AS MarketType,
    m.Country AS MarketCountry
FROM Stocks s
JOIN Market m ON s.MarketId = m.MarketId;

CREATE VIEW ViewBrokerCommission AS
SELECT 
    PlatformId,
    Name AS BrokerName,
    MobileNumber,
    Website,
    Commission AS CommissionRate
FROM BrokerPlatform;

CREATE VIEW ViewStockTransactions AS
SELECT 
    b.BuyerId,
    b.Name AS BuyerName,
    s.StockId,
    s.StockName,
    p.Quantity,
    p.PurchasePrice,
    (p.Quantity * p.PurchasePrice) AS TotalValue
FROM Buyer b
JOIN Portfolio p ON b.BuyerId = p.BuyerId
JOIN Stocks s ON p.StockId = s.StockId;

CREATE VIEW ViewDividendsPaid AS
SELECT 
    d.DividendId,
    b.BuyerId,
    b.Name AS BuyerName,
    d.Date AS DividendDate,
    d.Amount AS DividendAmount
FROM Dividend d
JOIN Buyer b ON d.BuyerId = b.BuyerId;

CREATE VIEW ViewBuyersWithKYCStatus AS
SELECT 
    BuyerId,
    Name AS BuyerName,
    Email,
    MobileNumber,
    KYCStatus,
    PANNo,
    LinkedBankAccount,
    DematAccount,
    Capital
FROM Buyer;

CREATE VIEW ViewPlatformStockUpdates AS
SELECT 
    u.StockId,
    s.StockName,
    u.PlatformId,
    bp.Name AS BrokerPlatform
FROM Updates u
JOIN Stocks s ON u.StockId = s.StockId
JOIN BrokerPlatform bp ON u.PlatformId = bp.PlatformId;
