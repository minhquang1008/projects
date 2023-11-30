/*YTD - BOM - PhaiSinh*/

/*Trailing - Fee Income (So sánh 5 năm gần nhất) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATETIMEFROMPARTS(YEAR(@Date)-4,1,1,0,0,0,0);

WITH 

[BranchList] AS (
	SELECT [BranchID]
	FROM [BranchTargetByYear] 
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Fee Income'
)

, [YearlyTarget] AS (
    SELECT 
		[Year]
        , CAST(SUM(CAST([Target] AS FLOAT)) AS DECIMAL(30,8)) [Target]
    FROM [DWH-AppData].[dbo].[BMD.FDSTarget]
	WHERE [Year] BETWEEN YEAR(@Since) AND YEAR(@Date)
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
		DATETIMEFROMPARTS(YEAR([RRE0018].[Ngay]),12,31,0,0,0,0) [Date]
		, ISNULL(SUM([RRE0018].[PhiGiaoDichPHSThu]), 0) [Value]
	FROM [RRE0018]
	LEFT JOIN [Rel]
        ON [Rel].[AccountCode] = [RRE0018].[SoTaiKhoan]
		AND [Rel].[Date] = [RRE0018].[Ngay]
	WHERE [RRE0018].[Ngay] BETWEEN @Since AND @Date
		AND [Rel].[BranchID] IN (SELECT [BranchID] FROM [BranchList])
	GROUP BY DATETIMEFROMPARTS(YEAR([RRE0018].[Ngay]),12,31,0,0,0,0)
)

SELECT
	DATETIMEFROMPARTS([YearlyTarget].[Year],12,31,0,0,0,0) [Date]
	, ISNULL([ValueAllBranchesByDate].[Value], 0) [Actual]
	, ISNULL([YearlyTarget].[Target], 0) [Target]
FROM [YearlyTarget]
LEFT JOIN [ValueAllBranchesByDate]
	ON YEAR([ValueAllBranchesByDate].[Date]) = [YearlyTarget].[Year]
ORDER BY 1


END