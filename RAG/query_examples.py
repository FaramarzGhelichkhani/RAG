
def get_query_examples():

    examples = [
        {"input":"مشتریانی که در یک ساله گذشته بیش از ده بار صندوق عیار را خرید کرده اند. صندوق عیار یک صندوق ای تی اف است که ایشور کی آن 12052 می باشد.", 
        "output": """ select dc.customerCode  from dbo.facttrade  df
    join dbo.DimIssuer di on di.stockKey = df.stockKey  
    join dbo.DimDate dd on dd.dateKey  = df.tradeDateKey
    join pub.DimCustomer_VC dc on dc.customerKey = df.customerKey
    where di.issuerKey = 12052 
    and dd.dateId > (select dateId - 365 from dbo.DimDate where dateKey = (select max(tradeDateKey) from dbo.facttrade))
    and tradeSideKey = 1 and df.quantity > 0
    group by dc.customerCode 
    having count(df.tradeId) > 10 """},

    {"input":". تعداد مشتریانی که بیشتر از هیجده سال سن دارند. از جدول هاب کاستومر استفاده کن. تاریخ مورد نظر برای محاسبه 14031130 می باشد", 
    "output":"SELECT COUNT(*) AS CustomerCount FROM pub.HubCustomer_VC AS h JOIN dbo.DimDate AS d ON d.dateKey = h.birthDateKey WHERE h.partyTypeCode = 1 AND (14031130 / 10000 - d.yearNo) >= 18"},
    
    {"input": "پرتفو آنلاین و ای تی اف مشتریان در روز (dateKey)14031201",
     "output":"""  SELECT h.customerCode, SUM(f.quantity * di.vwaPrice) AS totalPortfolioValue 
      FROM dbo.FactPortfolioLatest f 
      JOIN pub.HubCustomer_VC h ON f.customerKey = h.customerKey 
      JOIN dbo.FactDailyIssuerIndex di ON f.issuerKey = di.issuerKey 
      where  f.fromDateKey <= 14031201 AND f.toDateKey > 14031201 and f.quantity > 0 
      GROUP BY h.customerCode;"""},

    {"input":"پرتفو صندوق های صدروی ابطالی در روز 14031201(dateKey)",
     "output":""" SELECT c.customerCode, SUM(CASE WHEN p.fundKey IN (1, 2) THEN p.quantity * f.sellNAV ELSE 0 END) AS cashPortfolio, 
SUM(CASE WHEN p.fundKey NOT IN (1, 2) THEN p.quantity * f.sellNAV ELSE 0 END) AS otherPortfolio, 
SUM(p.quantity * f.sellNAV) AS totalPortfolio 
FROM db_invest.FactPortfolioMutualFund p 
JOIN db_invest.DimCustomerFund cf ON p.investorId = cf.investorId AND p.fundKey = cf.fundKey 
JOIN pub.HubCustomer_VC c ON cf.customerKey = c.customerKey 
JOIN dbo.FactDailyFund f ON (p.fundKey = f.fundKey OR (p.fundKey = 10 AND f.fundKey = 9)) AND f.fundDateKey = 14031201
WHERE p.fromDateKey <= 14031201 AND p.toDateKey >= 14031201 
GROUP BY c.customerCode; """}
    ]

    return examples