/*YTD - BOM - CoSo*/

/*Actual vs Target - Fee Income (Phí giao dịch - Thực tế và chỉ tiêu) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfYear DATETIME;
SET @FirstDateOfYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

WITH

[TargetByBranch] AS (
    SELECT 
        [BranchID] 
        , CAST([Target] AS FLOAT) [FeeIncome]
    FROM [DWH-AppData].[dbo].[BMD.FlexTarget]
    WHERE [Year] = YEAR(@Date)
        AND [Measure] = 'Fee Income'
)

, [BranchActual] AS (
    SELECT 
        [relationship].[branch_id] [BranchID]
        , SUM([trading_record].[fee]) [FeeIncome]
    FROM [trading_record]
    LEFT JOIN [relationship]
        ON [trading_record].[date] = [relationship].[date]
        AND [trading_record].[sub_account] = [relationship].[sub_account]
    WHERE [trading_record].[date] BETWEEN @FirstDateOfYear AND @Date
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
    GROUP BY [relationship].[branch_id]
)

SELECT
	[TargetByBranch].[BranchID]
	, ISNULL([BranchActual].[FeeIncome],0) [Actual]
    , [TargetByBranch].[FeeIncome] [Target]
FROM [TargetByBranch]
LEFT JOIN [BranchActual]
    ON [TargetByBranch].[BranchID] = [BranchActual].[BranchID]
ORDER BY 1


END
