/*MTD - BOM - PhaiSinh*/

/*Fluctuation - Fee Income (Biến động phí giao dịch) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Since DATETIME;
SET @Since = DATEADD(DAY,1,EOMONTH(DATEADD(YEAR,-1,@Date)));

WITH

[TargetByBranch] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Fee Income'
)

, [WorkDays] AS (
	SELECT
		[Date]
		, CASE 
			WHEN ISDATE(CONCAT(YEAR([Date]),'-',MONTH([Date]),'-',DAY(@Date))) = 1 
				THEN DATETIMEFROMPARTS(YEAR([Date]),MONTH([Date]),DAY(@Date),0,0,0,0)
			ELSE EOMONTH(DATETIMEFROMPARTS(YEAR([Date]),MONTH([Date]),1,0,0,0,0)) 
		END [EndOfPeriod]
	FROM [Date]
	WHERE [Work] = 1
		AND [Date] BETWEEN @Since AND @Date
		AND DAY([Date]) <= DAY(@Date)
)

, [Index] AS (
	SELECT 
		[WorkDays].[Date]
		, [WorkDays].[EndOfPeriod]
		, [TargetByBranch].[BranchID]
	FROM [TargetByBranch] CROSS JOIN [WorkDays]
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

, [RawResult] AS (
	SELECT
		[RRE0018].[Ngay] [Date]
		, [Rel].[BranchID]
		, ISNULL(SUM([RRE0018].[PhiGiaoDichPHSThu]), 0) [FeeIncome]
	FROM [RRE0018]
	LEFT JOIN [Rel]
		ON [RRE0018].[Ngay] = [Rel].[Date]
		AND [RRE0018].[SoTaiKhoan] = [Rel].[AccountCode]
	GROUP BY [RRE0018].[Ngay], [Rel].[BranchID]
)

SELECT
	[Index].[EndOfPeriod] [Date]
	, ISNULL(SUM([RawResult].[FeeIncome]), 0) [Value]
FROM [Index]
LEFT JOIN [RawResult]
	ON [RawResult].[Date] = [Index].[Date]
	AND [RawResult].[BranchID] = [Index].[BranchID]
GROUP BY [Index].[EndOfPeriod]
ORDER BY [Index].[EndOfPeriod]


END
