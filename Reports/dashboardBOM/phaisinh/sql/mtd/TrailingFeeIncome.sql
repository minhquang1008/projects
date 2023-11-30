/*MTD - BOM - PhaiSinh*/

/*Trailing - Fee Income (So sánh 12 tháng gần nhất) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATEADD(DAY,1,EOMONTH(DATEADD(YEAR,-1,@Date)));

WITH 

[BranchList] AS (
	SELECT [BranchID]
	FROM [BranchTargetByYear] 
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Fee Income'
)

, [MonthlyTarget] AS (
    SELECT 
		[Year]
        , CAST(SUM(CAST([Target] AS FLOAT)) / 12 AS DECIMAL(30,8)) [Target]
    FROM [DWH-AppData].[dbo].[BMD.FDSTarget]
	WHERE [Year] IN (YEAR(@Since), YEAR(@Date))
        AND [Measure] = 'Fee Income'
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
		, ISNULL(SUM([RRE0018].[PhiGiaoDichPHSThu]), 0) [Actual]
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
	, [ValueAllBranchesByDate].[Actual]
	, [MonthlyTarget].[Target]
FROM [MonthlyTarget]
LEFT JOIN [ValueAllBranchesByDate]
	ON YEAR([ValueAllBranchesByDate].[Date]) = [MonthlyTarget].[Year]
ORDER BY 1


END