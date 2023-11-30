/*MTD - BOM - PhaiSinh*/

/*Trailing - Market Share (So sánh 12 tháng gần nhất)*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATEADD(DAY,1,EOMONTH(DATEADD(YEAR,-1,@Date)));


WITH 

[MarketTradingValue] AS (
	SELECT
		EOMONTH([Txdate]) [Date]
		, SUM(ISNULL([FDS_MarketInfo].[MkTradingVol],0)) [TotalContracts]
	FROM [DWH-CoSo].[dbo].[FDS_MarketInfo]
	WHERE [Txdate] BETWEEN @Since AND @Date 
	GROUP BY EOMONTH([Txdate])
)

, [BranchList] AS (
	SELECT [BranchID]
	FROM [BranchTargetByYear] 
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Market Share'
)

, [MonthlyTarget] AS (
    SELECT
        [Year]
        , CAST(SUM(CAST([Target] AS FLOAT)) AS DECIMAL(30,8)) [Target]
    FROM [DWH-AppData].[dbo].[BMD.FDSTarget]
	WHERE [Year] IN (YEAR(@Since), YEAR(@Date))
        AND [Measure] = 'Market Share'
	GROUP BY [Year]
)

, [Rel] AS (
    SELECT DISTINCT
		[date] [Date]
 		, [branch_id] [BranchID]
		, [broker_id] [BrokerID]
		, [account_code] [AccountCode]
	FROM [relationship]
    WHERE [date] BETWEEN @Since AND @Date
)

, [ValueAllBranchesByDate] AS (
	SELECT
		EOMONTH([RRE0018].[Ngay]) [Date]
		, SUM([RRE0018].[SoLuongHopDong]) [Value]
	FROM [RRE0018]
	LEFT JOIN [Rel]
        ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
	WHERE [RRE0018].[Ngay] BETWEEN @Since AND @Date
		AND [Rel].[BranchID] IN (SELECT [BranchID] FROM [BranchList])
	GROUP BY EOMONTH([RRE0018].[Ngay])
)

SELECT
	[ValueAllBranchesByDate].[Date]
	, ISNULL([ValueAllBranchesByDate].[Value] / [MarketTradingValue].[TotalContracts] / 2, 0) [Actual]
	, ISNULL([MonthlyTarget].[Target], 0) [Target]
FROM [MonthlyTarget]
LEFT JOIN [ValueAllBranchesByDate]
	ON YEAR([ValueAllBranchesByDate].[Date]) = [MonthlyTarget].[Year]
LEFT JOIN [MarketTradingValue]
	ON [ValueAllBranchesByDate].[Date] = [MarketTradingValue].[Date]
ORDER BY 1


END