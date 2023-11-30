/*YTD - BOM - CoSo*/

/*Trailing - Fee Income (So sánh 5 năm gần nhất)*/

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
        , SUM(CAST([Target] AS FLOAT)) [Target]
	FROM [DWH-AppData].[dbo].[BMD.FlexTarget]
	WHERE [Year] BETWEEN YEAR(@Since) AND YEAR(@Date)
        AND [Measure] = 'Fee Income'
	GROUP BY [Year]
)

, [ValueAllBranchesByDate] AS (
	SELECT
		DATETIMEFROMPARTS(YEAR([trading_record].[date]),12,31,0,0,0,0) [Date]
		, SUM([trading_record].[fee]) [Actual]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[date] = [trading_record].[date]
		AND [relationship].[sub_account] = [trading_record].[sub_account]
	WHERE [trading_record].[date] BETWEEN @Since AND @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [BranchList])
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
	GROUP BY DATETIMEFROMPARTS(YEAR([trading_record].[date]),12,31,0,0,0,0)
)

SELECT
	[ValueAllBranchesByDate].[Date]
	, [ValueAllBranchesByDate].[Actual]
	, [YearlyTarget].[Target]
FROM [YearlyTarget]
LEFT JOIN [ValueAllBranchesByDate]
	ON YEAR([ValueAllBranchesByDate].[Date]) = [YearlyTarget].[Year]
ORDER BY 1


END
