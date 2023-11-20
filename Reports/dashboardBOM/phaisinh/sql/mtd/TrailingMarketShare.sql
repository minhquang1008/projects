/*MTD - BOM - PhaiSinh*/

/*Trailing - Market Share (So sánh 12 tháng gần nhất) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATEADD(DAY,1,EOMONTH(DATEADD(YEAR,-1,@Date)));


WITH 

[MarketTradingValue] AS (
	SELECT
		EOMONTH([Ngay]) [Date]
		, SUM(ISNULL([KhoiLuongKhopLenh],0) + ISNULL([KhoiLuongThoaThuan],0)) [TotalContracts]
	FROM [DWH-ThiTruong].[dbo].[KetQuaGiaoDichPhaiSinhVietStock]
	WHERE [Ngay] BETWEEN @Since AND @Date 
	GROUP BY EOMONTH([Ngay])
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
        , CAST(SUM([Target]) AS DECIMAL(20,7)) [Target]
    FROM [BranchTargetByYear] 
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
	, [ValueAllBranchesByDate].[Value] / [MarketTradingValue].[TotalContracts] / 2 [Actual]
	, [MonthlyTarget].[Target]
FROM [MonthlyTarget]
LEFT JOIN [ValueAllBranchesByDate]
	ON YEAR([ValueAllBranchesByDate].[Date]) = [MonthlyTarget].[Year]
LEFT JOIN [MarketTradingValue]
	ON [ValueAllBranchesByDate].[Date] = [MarketTradingValue].[Date]
ORDER BY 1


END